from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Literal, Union, Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from CreeDictionary.API.schema import SerializedDefinition
from CreeDictionary.utils import (
    shared_res_dir,
)

from morphodict.analysis import RichAnalysis

# How long a wordform or dictionary head can be. Not actually enforced in SQLite.
MAX_WORDFORM_LENGTH = 60

logger = logging.getLogger(__name__)


class WordformLemmaManager(models.Manager):
    """We are essentially always going to want the lemma

    So make preselecting it the default.
    """

    def get_queryset(self):
        return super().get_queryset().select_related("lemma")


# This type is the int pk for a saved wordform, or (text, analysis) for an unsaved one.
WordformKey = Union[int, tuple[str, str]]


class DiacriticPreservingJsonEncoder(DjangoJSONEncoder):
    """Stores Unicode strings, e.g., "pê", in the database

    Instead of ASCII-fied "p\u00ea".
    """

    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, "ensure_ascii": False}
        super().__init__(*args, **kwargs)


class Wordform(models.Model):
    # Queries always do .select_related("lemma"):
    objects = WordformLemmaManager()

    text = models.CharField(max_length=MAX_WORDFORM_LENGTH)

    raw_analysis = models.JSONField(null=True, encoder=DiacriticPreservingJsonEncoder)

    paradigm = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        null=True,
        blank=False,
        default=None,
        help_text="If provided, this is the name of a static paradigm that this "
        "wordform belongs to. This name should match the filename in "
        "res/layouts/static/ WITHOUT the file extension.",
    )

    is_lemma = models.BooleanField(
        default=False,
        help_text="The wordform is chosen as lemma. This field defaults to true if according to fst the wordform is not"
        " analyzable or it's ambiguous",
    )

    lemma = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="inflections",
        help_text="The identified lemma of this wordform. Defaults to self",
        # This will never actually be null, but only the import creates wordforms, so this should be ok
        # self-referential blah blah blah
        null=True,
    )

    slug = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        unique=True,
        null=True,
        help_text="""
            A stable unique identifier for a lemma. Used in public-facing URLs,
            and for import reconciliation.
        """,
    )

    linguist_info = models.JSONField(
        blank=True,
        help_text="""
            Various pieces of information about wordforms/lemmas that are of
            interest to linguists, and are available for display in templates,
            but that are not used by any of the logic in the morphodict code.
        """,
    )

    class Meta:
        indexes = [
            # analysis is for faster user query (see search/lookup.py)
            models.Index(fields=["raw_analysis"]),
            # text index benefits fast wordform matching (see search/lookup.py)
            models.Index(fields=["text"]),
            # When we *just* want to lookup text wordforms that are "lemmas"
            # (Note: Eddie thinks "head words" may also be lumped in as "lemmas")
            # Used by:
            #  - affix tree intialization
            #  - sitemap generation
            models.Index(fields=["is_lemma", "text"]),
            # pos and inflectional_category are used when generating the preverb cache:
            # models.Index(fields=["inflectional_category"]),
            # models.Index(fields=["pos"]),
        ]

        constraints: list[Any] = [
            # models.UniqueConstraint(
            #     fields=("text", "analysis"),
            #     name="text_analysis_unique",
            #     condition=Q(analysis__isnull=False),
            # )
        ]

    def __str__(self):
        return self.text

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name}: {self.text} {self.analysis}>"

    @property
    def analysis(self):
        if self.raw_analysis is None:
            return None
        return RichAnalysis(self.raw_analysis)

    @property
    def key(self) -> WordformKey:
        """A value to check if objects represent the ‘same’ wordform

        Works even if the objects are unsaved.
        """
        if self.slug is not None:
            return self.slug
        if self.id is not None:
            return self.id
        return (self.text, self.analysis)

    def get_absolute_url(self, ambiguity: Literal["allow", "avoid"] = "avoid") -> str:
        """
        :return: url that looks like
         "/words/nipaw" "/words/nipâw?pos=xx" "/words/nipâw?inflectional_category=xx" "/words/nipâw?analysis=xx" "/words/nipâw?id=xx"
         it's the least strict url that guarantees unique match in the database
        """
        assert self.is_lemma, "There is no page for non-lemmas"
        return reverse("cree-dictionary-index-with-lemma", kwargs={"slug": self.slug})


class DictionarySource(models.Model):
    """
    Represents bibliographic information for a set of definitions.

    A Definition is said to cite a DictionarySource.
    """

    # A short, unique, uppercased ID. This will be exposed to users!
    #  e.g., CW for "Cree: Words"
    #     or MD for "Maskwacîs Dictionary"
    abbrv = models.CharField(max_length=8, primary_key=True)

    # Bibliographic information:
    title = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        help_text="What is the primary title of the dictionary source?",
    )
    author = models.CharField(
        max_length=512,
        blank=True,
        help_text="Separate multiple authors with commas. See also: editor",
    )
    editor = models.CharField(
        max_length=512,
        blank=True,
        help_text=(
            "Who edited or compiled this volume? "
            "Separate multiple editors with commas."
        ),
    )
    year = models.IntegerField(
        null=True, blank=True, help_text="What year was this dictionary published?"
    )
    publisher = models.CharField(
        max_length=128, blank=True, help_text="What was the publisher?"
    )
    city = models.CharField(
        max_length=64, blank=True, help_text="What is the city of the publisher?"
    )

    def __str__(self):
        """
        Will print a short citation like:

            [CW] “Cree : Words” (Ed. Arok Wolvengrey)
        """
        # These should ALWAYS be present
        abbrv = self.abbrv
        title = self.title

        # Both of these are optional:
        author = self.author
        editor = self.editor

        author_or_editor = ""
        if author:
            author_or_editor += f" by {author}"
        if editor:
            author_or_editor += f" (Ed. {editor})"

        return f"[{abbrv}]: “{title}”{author_or_editor}"


class Definition(models.Model):
    text = models.CharField(max_length=200)

    # A definition **cites** one or more dictionary sources.
    citations = models.ManyToManyField(DictionarySource)

    # A definition defines a particular wordform
    wordform = models.ForeignKey(
        Wordform, on_delete=models.CASCADE, related_name="definitions"
    )

    # If this definition is auto-generated based on a different definition,
    # point at the source definition.
    auto_translation_source = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True
    )

    # Why this property exists:
    # because DictionarySource should be its own model, but most code only
    # cares about the source IDs. So this removes the coupling to how sources
    # are stored and returns the source IDs right away.
    @property
    def source_ids(self) -> list[str]:
        """
        A tuple of the source IDs that this definition cites.
        """
        return sorted(set(c.abbrv for c in self.citations.all()))

    def serialize(self) -> SerializedDefinition:
        """
        :return: json parsable format
        """
        return {"text": self.text, "source_ids": self.source_ids}

    def __str__(self):
        return self.text


class TargetLanguageKeyword(models.Model):
    text = models.CharField(max_length=MAX_WORDFORM_LENGTH)

    wordform = models.ForeignKey(
        Wordform, on_delete=models.CASCADE, related_name="target_language_keyword"
    )

    def __repr__(self) -> str:
        return f"<EnglishKeyword(text={self.text!r} of {self.wordform!r} ({self.id})>"

    class Meta:
        indexes = [models.Index(fields=["text"])]


class SourceLanguageKeyword(models.Model):
    """Variant spellings for source-language items that do not have an analysis.

    When searching for things that do have an analysis, the relaxed analyzer can
    handle spelling variations, differences in diacritics, and so on.

    For things that aren’t analyzable—Cree preverbs for now, maybe phrases
    later—we store variants here, such as the version without diacritics, so
    that they’re still searchable even if what the user typed in isn’t exact.
    """

    text = models.CharField(max_length=MAX_WORDFORM_LENGTH)

    wordform = models.ForeignKey(Wordform, on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=["text"])]


class _WordformCache:
    @cached_property
    def MORPHEME_RANKINGS(self) -> Dict[str, float]:
        logger.debug("reading morpheme rankings")
        ret = {}

        lines = (
            Path(shared_res_dir / "W_aggr_corp_morph_log_freq.txt")
            .read_text()
            .splitlines()
        )
        for line in lines:
            cells = line.split("\t")
            # todo: use the third row
            if len(cells) >= 2:
                freq, morpheme, *_ = cells
                ret[morpheme] = float(freq)
        return ret

    def preload(self):
        # Accessing these cached properties will preload them
        self.MORPHEME_RANKINGS


wordform_cache = _WordformCache()
