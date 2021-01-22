import logging
import typing
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

from django.db import models, transaction
from django.db.models import Max
from django.forms import model_to_dict
from django.urls import reverse
from django.utils.functional import cached_property
from paradigm import Layout
from shared import expensive
from sortedcontainers import SortedSet
from utils import ParadigmSize, PartOfSpeech, WordClass, fst_analysis_parser
from utils.fst_analysis_parser import LABELS
from utils.types import FSTTag

from .schema import SerializedDefinition, SerializedWordform

# Don't start evicting cache entries until we've seen over this many unique definitions:
MAX_SOURCE_ID_CACHE_ENTRIES = 4096

# Avoid a runtime circular-dependency;
# without this line,
#  - model.py imports search.py; and,
#  - search.py imports model.py 💥
if typing.TYPE_CHECKING:
    from .search import SearchResult


logger = logging.getLogger(__name__)


class Wordform(models.Model):
    # this is initialized upon app ready.
    # this helps speed up preverb match
    # will look like: {"pe": {...}, "e": {...}, "nitawi": {...}}
    # pure MD content won't be included
    PREVERB_ASCII_LOOKUP: Dict[str, Set["Wordform"]] = defaultdict(set)

    # this is initialized upon app ready.
    MORPHEME_RANKINGS: Dict[str, float] = {}

    def get_absolute_url(self) -> str:
        """
        :return: url that looks like
         "/words/nipaw" "/words/nipâw?pos=xx" "/words/nipâw?inflectional_category=xx" "/words/nipâw?analysis=xx" "/words/nipâw?id=xx"
         it's the least strict url that guarantees unique match in the database
        """
        assert self.is_lemma, "There is no page for non-lemmas"
        lemma_url = reverse(
            "cree-dictionary-index-with-lemma", kwargs={"lemma_text": self.text}
        )
        if self.homograph_disambiguator is not None:
            lemma_url += f"?{self.homograph_disambiguator}={quote(str(getattr(self, self.homograph_disambiguator)))}"

        return lemma_url

    def serialize(self) -> SerializedWordform:
        """
        Intended to be passed in a JSON API or into templates.

        :return: json parsable result
        """
        result = model_to_dict(self)
        result["definitions"] = [
            definition.serialize() for definition in self.definitions.all()
        ]
        result["lemma_url"] = self.get_absolute_url()

        # Displayed in the word class/inflection help:
        result["inflectional_category_plain_english"] = LABELS.english.get(
            self.inflectional_category
        )
        result["inflectional_category_linguistic"] = LABELS.linguistic_long.get(
            self.inflectional_category
        )
        result["wordclass_emoji"] = self.get_emoji_for_cree_wordclass()
        result["wordclass"] = self.wordclass_text

        return result

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

    @cached_property
    def homograph_disambiguator(self) -> Optional[str]:
        """
        :return: the least strict field name that guarantees unique match together with the text field.
            could be pos, inflectional_category, analysis, id or None when the text is enough to disambiguate
        """
        homographs = Wordform.objects.filter(text=self.text)
        if homographs.count() == 1:
            return None
        for field in "pos", "inflectional_category", "analysis":
            if homographs.filter(**{field: getattr(self, field)}).count() == 1:
                return field
        return "id"  # id always guarantees unique match

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

    def get_paradigm_layouts(
        self, size: ParadigmSize = ParadigmSize.BASIC
    ) -> List[Layout]:
        """
        :param size: How detail the paradigm table is
        """
        wc = fst_analysis_parser.extract_word_class(self.analysis)
        if wc is not None:
            tables = expensive.paradigm_filler.fill_paradigm(self.text, wc, size)
        else:
            tables = []
        return tables

    @property
    def md_only(self) -> bool:
        """
        check if the wordform instance has only definition from the MD source
        """
        for definition in self.definitions.all():
            if set(definition.source_ids) - {"MD"}:
                return False
        return True

    # override pk to allow use of bulk_create
    # auto-increment is also implemented in the overridden save() method below
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=40)

    inflectional_category = models.CharField(
        max_length=10,
        help_text="Inflectional category directly from source xml file",  # e.g. NI-3
    )
    RECOGNIZABLE_POS = [(pos.value,) * 2 for pos in PartOfSpeech] + [("", "")]
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
            # analysis is for faster user query (see search.py)
            models.Index(fields=["analysis"]),
            # text index benefits fast wordform matching (see search.py)
            models.Index(fields=["text"]),
        ]

    def __str__(self):
        return self.text

    def __repr__(self):
        cls_name = type(self).__name__
        return f"<{cls_name}: {self.text} {self.analysis}>"

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

    @staticmethod
    def search_with_affixes(query: str) -> SortedSet["SearchResult"]:
        """
        Search for wordforms matching:
         - the wordform text
         - the definition keyword text
         - affixes of the wordform text
         - affixes of the definition keyword text
        """
        from .search import WordformSearchWithAffixes

        search = WordformSearchWithAffixes(query)
        return search.perform()

    @staticmethod
    def simple_search(query: str) -> SortedSet["SearchResult"]:
        """
        Search, trying to match full wordforms or keywords within definitions.

        Does NOT try to match affixes!
        """
        from .search import WordformSearchWithExactMatch

        search = WordformSearchWithExactMatch(query)
        return search.perform()


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

    # Why this property exists:
    # because DictionarySource should be its own model, but most code only
    # cares about the source IDs. So this removes the coupling to how sources
    # are stored and returns the source IDs right away.
    @property
    def source_ids(self) -> Tuple[str, ...]:
        """
        A tuple of the source IDs that this definition cites.
        """
        return get_all_source_ids_for_definition(self.id)

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


@lru_cache(maxsize=MAX_SOURCE_ID_CACHE_ENTRIES)
def get_all_source_ids_for_definition(definition_id: int) -> Tuple[str, ...]:
    """
    Returns all of the dictionary source IDs (e.g., "MD", "CW").
    This is cached so to reduce the amount of duplicate queries made to the database,
    especially during serialization.

    See:
     - https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/pull/558
     - https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/531
    """
    dfn = Definition.objects.get(pk=definition_id)
    return tuple(sorted(source.abbrv for source in dfn.citations.all()))
