from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Literal, Union

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
MAX_TEXT_LENGTH = 200

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

    fst_lemma = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        null=True,
        help_text="""
            The form to use for generating wordforms of this lemma using the
            generator FST. Should only be set for lemmas.
         """,
    )

    paradigm = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        null=True,
        blank=False,
        default=None,
        help_text="""
            If provided, this is the name of a paradigm that this wordform belongs
            to. This name must match the filename or directory in res/layouts/
            (without the file extension).
        """,
    )

    is_lemma = models.BooleanField(
        default=False, help_text="Whether this wordform is a lemma"
    )

    lemma = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="inflections",
        help_text="The lemma of this wordform",
        # This field should never be null, but since the field is
        # self-referential, we have to allow it to be declared nullable so that
        # the import process can first save an initial wordform object without a
        # lemma, and then save the auto-generated ID into the lemma field.
        null=True,
    )

    slug = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        unique=True,
        null=True,
        help_text="""
            A stable unique identifier for a lemma. Used in public-facing URLs,
            and for import reconciliation. It is recommended to use the wordform
            text, optionally followed by ‘@’ and some sort of homograph
            disambiguation string.
        """,
    )

    linguist_info = models.JSONField(
        blank=True,
        null=True,
        help_text="""
            Various pieces of information about wordforms/lemmas that are of
            interest to linguists, and are available for display in templates,
            but that are not used by any of the logic in the morphodict code.
        """,
    )

    import_hash = models.CharField(
        max_length=MAX_WORDFORM_LENGTH,
        null=True,
        help_text="""
            A hash of the input JSON, used to determine whether to update an
            entry or not. Only valid on lemmas.
        """,
    )

    class Meta:
        indexes = [
            models.Index(fields=["text", "raw_analysis"]),
            # When we *just* want to lookup text wordforms that are "lemmas"
            # Used by:
            #  - affix tree intialization
            #  - sitemap generation
            models.Index(fields=["is_lemma", "text"]),
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
        # FIXME: will return '/word/None' if no slug
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

    def __str__(self):
        return self.abbrv


class Definition(models.Model):
    text = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        help_text="""
            The definition text. This is displayed to the user, and terms within
            it are indexed for full-text search.
        """,
    )

    raw_core_definition = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        null=True,
        help_text="""
            The definition to optionally use for auto-translation.

            It should include only the core sense of the wordform without any
            notes or cross-references.
        """,
    )
    raw_semantic_definition = models.CharField(
        max_length=MAX_TEXT_LENGTH,
        null=True,
        help_text="""
            The definition to optionally use when building a semantic vector.

            This is not visible to the user. It may include etymological terms,
            and may omit stopwords.

            Even though it is only used at import time, it is stored in the
            database to enable the possibility of regenerating definition
            vectors without the original importjson file.
        """,
    )

    @property
    def core_definition(self):
        """
        Return the core definition, or the standard definition text if no
        explicit core definition has been provided.
        """
        if self.raw_core_definition is not None:
            return self.raw_core_definition
        return self.text

    @property
    def semantic_definition(self):
        """
        Return the semantic definition, or the standard definition text if no
        explicit core definition has been provided.
        """
        if self.raw_semantic_definition is not None:
            return self.raw_semantic_definition
        return self.text

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
        return {
            "text": self.text,
            "source_ids": self.source_ids,
            "is_auto_translation": self.auto_translation_source_id is not None,
        }

    def __str__(self):
        return self.text


class TargetLanguageKeyword(models.Model):
    text = models.CharField(max_length=MAX_WORDFORM_LENGTH)

    wordform = models.ForeignKey(
        Wordform, on_delete=models.CASCADE, related_name="target_language_keyword"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text", "wordform_id"], name="target_kw_text_and_wordform"
            )
        ]
        indexes = [models.Index(fields=["text"])]

    def __repr__(self) -> str:
        return f"<TargetLanguageKeyword(text={self.text!r} of {self.wordform!r} ({self.id})>"


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
        constraints = [
            models.UniqueConstraint(
                fields=["text", "wordform_id"], name="source_kw_text_and_wordform"
            )
        ]
        indexes = [
            models.Index(
                fields=["text"],
            )
        ]

    def __repr__(self) -> str:
        return f"<SourceLanguageKeyword(text={self.text!r} of {self.wordform!r} ({self.id})>"


class ImportStamp(models.Model):
    """Holds timestamp of the last import

    This table that should only ever have at most a single row.
    """

    timestamp = models.FloatField(help_text="epoch time of import")


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
