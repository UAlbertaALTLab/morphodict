from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, Literal, Optional, Union
from urllib.parse import quote

from django.db import models, transaction
from django.db.models import Max, Q
from django.urls import reverse
from django.utils.functional import cached_property
from CreeDictionary.utils import (
    PartOfSpeech,
    WordClass,
    fst_analysis_parser,
    shared_res_dir,
)
from CreeDictionary.utils.cree_lev_dist import remove_cree_diacritics
from CreeDictionary.utils.types import FSTTag

from CreeDictionary.CreeDictionary.relabelling import LABELS

from .schema import SerializedDefinition

# How long a wordform or dictionary head can be (number of Unicode scalar values)
# TODO: is this too small?
MAX_WORDFORM_LENGTH = 40

# Don't start evicting cache entries until we've seen over this many unique definitions:
MAX_SOURCE_ID_CACHE_ENTRIES = 4096

logger = logging.getLogger(__name__)


class WordformLemmaManager(models.Manager):
    """We are essentially always going to want the lemma

    So make preselecting it the default.
    """

    def get_queryset(self):
        return super().get_queryset().select_related("lemma")


# This type is the int pk for a saved wordform, or (text, analysis) for an unsaved one.
WordformKey = Union[int, tuple[str, str]]


class Wordform(models.Model):
    # Queries always do .select_related("lemma"):
    objects = WordformLemmaManager()

    RECOGNIZABLE_POS = [(pos.value,) * 2 for pos in PartOfSpeech] + [("", "")]

    # override pk to allow use of bulk_create
    # auto-increment is also implemented in the overridden save() method below
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=MAX_WORDFORM_LENGTH)

    inflectional_category = models.CharField(
        max_length=10,
        help_text="Inflectional category directly from source xml file",  # e.g. NI-3
    )

    pos = models.CharField(
        max_length=4,
        choices=RECOGNIZABLE_POS,
        help_text="Part of speech parsed from source. Can be unspecified",
    )

    analysis = models.CharField(
        max_length=50,
        default="",
        help_text="fst analysis or the best possible generated if the source is not analyzable",
        # see xml_importer.py::generate_as_is_analysis
    )

    paradigm = models.CharField(
        max_length=50,
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

    # if as_is is False. pos field is guaranteed to be not empty
    # and will be values from `constants.POS` enum class

    # if as_is is True, inflectional_category and pos fields can be under-specified, i.e. they can be empty strings
    as_is = models.BooleanField(
        default=False,
        help_text="The lemma of this wordform is not determined during the importing process."
        "is_lemma defaults to true and lemma field defaults to self",
    )

    lemma = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="inflections",
        help_text="The identified lemma of this wordform. Defaults to self",
    )

    # some lemmas have stems, they are shown in linguistic analysis
    # e.g. wâpam- is the stem for wâpamêw
    stem = models.CharField(
        max_length=128,
        blank=True,
    )

    class Meta:
        indexes = [
            # analysis is for faster user query (see search/lookup.py)
            models.Index(fields=["analysis"]),
            # text index benefits fast wordform matching (see search/lookup.py)
            models.Index(fields=["text"]),
            # When we *just* want to lookup text wordforms that are "lemmas"
            # (Note: Eddie thinks "head words" may also be lumped in as "lemmas")
            # Used by:
            #  - affix tree intialization
            #  - sitemap generation
            models.Index(fields=["is_lemma", "text"], name="lemma_text_idx"),
            # pos and inflectional_category are used when generating the preverb cache:
            models.Index(fields=["inflectional_category"]),
            models.Index(fields=["pos"]),
        ]

    def __str__(self):
        return self.text

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name}: {self.text} {self.analysis}>"

    def get_absolute_url(self, ambiguity: Literal["allow", "avoid"] = "avoid") -> str:
        """
        :return: url that looks like
         "/words/nipaw" "/words/nipâw?pos=xx" "/words/nipâw?inflectional_category=xx" "/words/nipâw?analysis=xx" "/words/nipâw?id=xx"
         it's the least strict url that guarantees unique match in the database
        """
        assert self.is_lemma, "There is no page for non-lemmas"
        lemma_url = reverse(
            "cree-dictionary-index-with-lemma", kwargs={"lemma_text": self.text}
        )

        if ambiguity == "allow":
            # avoids doing an expensive lookup to disambiguate
            return lemma_url

        if self.homograph_disambiguator is not None:
            lemma_url += f"?{self.homograph_disambiguator}={quote(str(getattr(self, self.homograph_disambiguator)))}"

        return lemma_url

    @property
    def wordclass_text(self) -> Optional[str]:
        """
        Returns the human readable text of the wordclass.

        Not to be confused with the poorly-named "word_class"
        """
        if enum := self.word_class:
            return enum.value
        # Every entry in the Cree Dictionary (itwêwina) SHOULD have an applicable
        # wordclass from crk.relabel.tsv.  So if everything is going well, this line
        # should never be reached:
        # TODO: should we crash with an assertion error instead?
        return None  # pragma: no cover

    def get_emoji_for_cree_wordclass(self) -> Optional[str]:
        """
        Attempts to get an emoji description of the full wordclass.
        e.g., "👤👵🏽" for "nôhkom"
        """
        maybe_word_class = self.word_class
        if maybe_word_class is None:
            return None
        fst_tag_str = maybe_word_class.to_fst_output_style().strip("+")
        tags = [FSTTag(t) for t in fst_tag_str.split("+")]
        return LABELS.emoji.get_longest(tags)

    # We do our own caching instead of using @cachedproperty so that we can
    # disambiguate homographs in bulk when displaying search results
    _cached_homograph_disambiguator: Optional[str]

    @property
    def homograph_disambiguator(self) -> Optional[str]:
        """
        :return: the least strict field name that guarantees unique match together with the text field.
            could be pos, inflectional_category, analysis, id or None when the text is enough to disambiguate
        """
        assert self.is_lemma

        if hasattr(self, "_cached_homograph_disambiguator"):
            return self._cached_homograph_disambiguator

        homographs = Wordform.objects.filter(text=self.text, is_lemma=True)
        key = self._compute_homograph_key(homographs)
        self._cached_homograph_disambiguator = key
        return key

    # TODO: rename! it should not have an underscore!
    @property
    def word_class(self) -> Optional[WordClass]:
        from_analysis = fst_analysis_parser.extract_word_class(self.analysis)
        if from_analysis:
            return from_analysis

        # Can't get it from the analysis? Maybe its the (deprecated) part-of-speech?
        try:
            return WordClass(self.pos)
        except ValueError:
            return None

    @property
    def key(self) -> WordformKey:
        """A value to check if objects represent the ‘same’ wordform

        Works even if the objects are unsaved.
        """
        if self.id is not None:
            return self.id
        return (self.text, self.analysis)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Ensure id is auto-incrementing.
        Infer foreign key 'lemma' to be self if self.is_lemma is set to True. (friendly to test creation)
        """
        max_id = Wordform.objects.aggregate(Max("id"))
        if max_id["id__max"] is None:
            self.id = 0
        else:
            self.id = max_id["id__max"] + 1

        # infer lemma if it is not set.
        # this helps with adding entries in django admin as the ui for
        # `lemma` takes forever to load.
        # Also helps with tests as it's now easier to create entries

        if self.is_lemma:
            self.lemma_id = self.id

        super(Wordform, self).save(*args, **kwargs)

    @classmethod
    def bulk_homograph_disambiguate(cls, wordform_objects: list[Wordform]):
        """Precache the homograph key information on the wordform_objects

        The information will be retrieved with a single database query.
        """
        wordform_texts = list(set(wf.text for wf in wordform_objects))
        homographs = Wordform.objects.filter(text__in=wordform_texts, is_lemma=True)
        by_text = defaultdict(list)
        for wf in homographs:
            by_text[wf.text].append(wf)
        for wf in wordform_objects:
            wf._cached_homograph_disambiguator = wf._compute_homograph_key(
                by_text[wf.text]
            )

    def _compute_homograph_key(self, all_wordforms_with_same_text):
        if len(all_wordforms_with_same_text) == 1:
            return None
        for field in "pos", "inflectional_category", "analysis":
            if (
                len(
                    [
                        wf
                        for wf in all_wordforms_with_same_text
                        if getattr(self, field) == getattr(wf, field)
                    ]
                )
                == 1
            ):
                return field
        return "id"  # id always guarantees unique match


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
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

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


class EnglishKeyword(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=20)

    # N.B., this says "lemma", but it can actually be ANY Wordform
    # (lemma or non-lemma)
    lemma = models.ForeignKey(
        Wordform, on_delete=models.CASCADE, related_name="english_keyword"
    )

    def __repr__(self) -> str:
        return f"<EnglishKeyword(text={self.text!r} of {self.lemma!r} ({self.id})>"

    class Meta:
        indexes = [models.Index(fields=["text"])]


class _WordformCache:
    @cached_property
    def PREVERB_ASCII_LOOKUP(self) -> dict[str, set[models.Wordform]]:
        logger.debug("initializing preverb search")
        # Hashing to speed up exhaustive preverb matching
        # will look like: {"pe": {...}, "e": {...}, "nitawi": {...}}
        # so that we won't need to search from the database every time the user searches for a preverb or when the user
        # query contains a preverb
        # An all inclusive filtering mechanism is inflectional_category=IPV OR pos="IPV". Don't rely on a single one
        # due to the inconsistent labelling in the source crkeng.xml.
        # e.g. for preverb "pe", the source gives pos=Ipc ic=IPV.
        # For "sa", the source gives pos=IPV ic="" (unspecified)
        # after https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/pull/262
        # many preverbs are normalized so that both inflectional_category and pos are set to IPV.

        def has_non_md_non_auto_definitions(wordform):
            "This may look slow, but isn’t if prefetch_related has been used"
            for d in wordform.definitions.all():
                for c in d.citations.all():
                    if c.abbrv not in ["auto", "MD"]:
                        return True
            return False

        lookup = defaultdict(set)
        queryset = Wordform.objects.filter(
            Q(inflectional_category="IPV") | Q(pos="IPV")
        ).prefetch_related("definitions__citations")
        for preverb_wordform in queryset:
            if has_non_md_non_auto_definitions(preverb_wordform):
                lookup[remove_cree_diacritics(preverb_wordform.text.strip("-"))].add(
                    preverb_wordform
                )
        return lookup

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
        self.PREVERB_ASCII_LOOKUP
        self.MORPHEME_RANKINGS


wordform_cache = _WordformCache()
