import logging
import unicodedata
from collections import defaultdict
from typing import Dict, List, NamedTuple, Set, Tuple, Iterable
from urllib.parse import unquote

from attr import attrib, attrs
from cree_sro_syllabics import syllabics2sro
from django.db import models, transaction
from django.db.models import F, Max, Q, QuerySet

from constants import SimpleLC, SimpleLexicalCategory, POS
from fuzzy_search import CreeFuzzySearcher
from shared import descriptive_analyzer_foma, normative_generator
from utils import fst_analysis_parser

logger = logging.getLogger(__name__)


def filter_cw_wordforms(q: QuerySet) -> Iterable["Wordform"]:
    """
    return the wordforms that has definition from CW dictionary

    :param q: a QuerySet of Wordforms
    """
    for wordform in q:
        for definition in wordform.definition_set.all():
            if "CW" in definition.source_ids:
                yield wordform
                break


@attrs(auto_attribs=True)
class SearchResult:
    """
    Contains all of the information needed to display a search result.
    """

    # the text of the match
    wordform: str

    part_of_speech: SimpleLC

    # Is this the lemma?
    is_lemma: bool

    # The text of the matched lemma
    lemma: str

    # Sequence of all preverb tags, in order
    preverbs: Tuple[str]

    # TODO: there are things to be figured out for this :/
    # Sequence of all reduplication tags present, in order
    reduplication_tags: Tuple[str]
    # Sequence of all initial change tags
    initial_change_tags: Tuple[str]

    definitions: Tuple["Definition"]

    @property
    def is_inflection(self) -> bool:
        """
        Is this an inflected form? That is, is this a wordform that is NOT the
        lemma?
        """
        return not self.is_lemma


class EntryKey(NamedTuple):
    """
    A wordform, its matched lemma, and the lexical category.
    """

    wordform: str
    lemma: str
    lc: SimpleLexicalCategory


class CreeAndEnglish(NamedTuple):
    """
    Duct tapes together two kinds of search results:

     - cree results -- a dict of analyses to the LEMMAS that match that analysis!
                    -- duplicate spellings are removed
     - english results -- a list of lemmas that match
    """

    cree_results: Dict[str, Set["Wordform"]]
    english_results: Set["Wordform"]


class Wordform(models.Model):
    _cree_fuzzy_searcher = None

    @classmethod
    def init_fuzzy_searcher(cls):
        if cls._cree_fuzzy_searcher is None:
            cls._cree_fuzzy_searcher = CreeFuzzySearcher(cls.objects.all())

    @classmethod
    def fuzzy_search(cls, query: str, distance: int) -> QuerySet:
        if cls._cree_fuzzy_searcher is None:
            return Wordform.objects.none()
        return cls._cree_fuzzy_searcher.search(query, distance)

    # override pk to allow use of bulk_create
    # auto-increment is also implemented in the overridden save below
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=40)

    full_lc = models.CharField(
        max_length=10,
        help_text="Full lexical category directly from source",  # e.g. NI-3
    )
    RECOGNIZABLE_POS = [(pos.value,) * 2 for pos in POS] + [("", "")]
    pos = models.CharField(
        max_length=4,
        choices=RECOGNIZABLE_POS,
        help_text="Part of speech parsed from source. Can be unspecified",
    )

    analysis = models.CharField(
        max_length=50,
        default="",
        help_text="fst analysis or the best possible generated if the source is not analyzable",  # see xml_importer.py::generate_as_is_analysis
    )
    is_lemma = models.BooleanField(
        default=False,
        help_text="The wordform is chosen as lemma. This field defaults to true if according to fst the wordform is not"
        " analyzable or it's ambiguous",
    )

    # if as_is is False. pos field is guaranteed to be not empty
    # and will be values from `constants.POS` enum class

    # if as_is is True, full_lc and pos fields can be under-specified, i.e. they can be empty strings
    as_is = models.BooleanField(
        default=False,
        help_text="It can not be determined whether this wordform is lemma or not during the importing process. "
        "is_lemma defaults to true and lemma field defaults to self",
    )

    lemma = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="inflections",
        help_text="The identified lemma of this wordform. Defaults to self",
    )

    class Meta:
        # analysis is for faster user query (in function fetch_lemma_by_user_query below)
        # text is for faster fuzzy search initialization when the app restarts on the server side (order_by text)
        # text index also benefits fast lemma matching in function fetch_lemma_by_user_query
        indexes = [models.Index(fields=["analysis"]), models.Index(fields=["text"])]

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
    def fetch_lemma_by_user_query(user_query: str) -> CreeAndEnglish:
        """
        treat the user query as cree and:

        Give the analysis of user query and matched lemmas.
        There can be multiple analysis for user queries
        One analysis could match multiple lemmas as well due to underspecified database fields.
        (lc and pos can be empty)

        treat the user query as English keyword and:

        Give a list of matched lemmas

        :param user_query: can be English or Cree (syllabics or not)
        """

        # Whitespace won't affect results, but the FST can't deal with it:
        user_query = user_query.strip()
        # Normalize to UTF8 NFC
        user_query = unicodedata.normalize("NFC", user_query)
        user_query = (
            user_query.replace("ā", "â")
            .replace("ē", "ê")
            .replace("ī", "î")
            .replace("ō", "ô")
        )
        user_query = syllabics2sro(user_query)

        user_query = user_query.lower()

        # build up result_lemmas in 2 ways
        # 1. spell relax in descriptive fst
        # 2. definition containment of the query word
        lemmas_by_analysis: Dict[str, List["Wordform"]] = defaultdict(list)

        # utilize the spell relax in descriptive_analyzer
        # TODO: use shared.descriptive_analyzer (HFSTOL) when this bug is fixed:
        # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
        fst_analyses: Set[str] = set(
            "".join(a) for a in descriptive_analyzer_foma.analyze(user_query)
        )

        # we choose to trust CW and show those matches with definition from CW
        as_is_matches: List["Wordform"] = []

        for analysis in fst_analyses:
            # todo: test

            exact_matched_wordform_ids = Wordform.objects.filter(
                analysis=analysis, is_lemma=True, as_is=False
            ).values("lemma__id")
            exact_matched_lemmas = Wordform.objects.filter(
                id__in=exact_matched_wordform_ids
            )

            if exact_matched_lemmas.exists():
                lemmas_by_analysis[analysis].extend(list(exact_matched_lemmas))
            else:
                # When the user query is outside of paradigm tables
                # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
                # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+Prs+3Sg'}
                # e.g. Err/Orth: ewapamat: {'PV/e+wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO+Err/Orth'

                lemma_lc = fst_analysis_parser.extract_lemma_and_category(analysis)
                if lemma_lc is None:
                    logger.error(
                        f"fst_analysis_parser cannot understand analysis {analysis}"
                    )
                    continue

                # Note:
                # non-analyzable matches should not be displayed (mostly from MD)
                # like "nipa", which means kill him
                # those results are filtered out by `as_is=False` below
                # suggested by Arok Wolvengrey

                lemma, lc = lemma_lc
                matched_lemmas = Wordform.objects.filter(text=lemma, is_lemma=True)
                if lc.pos is POS.PRON:
                    # specially handle pronouns.
                    # this is a temporary fix, otherwise "ôma" won't appear in the search results, since
                    # "ôma" has multiple analysis
                    # ôma+Ipc+Foc
                    # ôma+Pron+Dem+Prox+I+Sg
                    # ôma+Pron+Def+Prox+I+Sg
                    # it's ambiguous which one is the lemma in the importing process thus it's labeled "as_is"

                    # a more permanent fix requires every pronouns lemma to be listed and specified
                    lemmas_by_analysis[analysis].extend(
                        list(matched_lemmas.filter(pos="PRON"))
                    )
                else:
                    lemmas_by_analysis[analysis].extend(
                        list(matched_lemmas.filter(as_is=False, pos=lc.pos.name))
                    )

        # as per https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
        # preverbs should be presented
        # exhaustively search preverbs here (since we can't use fst on preverbs.)

        # for preverbs
        # A consistent filtering mechanism is full_lc=IPV OR pos="IPV". Don't rely on a single one
        # due to the inconsistent labelling in the source crkeng.xml.
        # e.g. for preverb "pe", the source gives pos=Ipc lc=IPV.
        # For "sa", the source gives pos=IPV lc="" (unspecified)

        # A imperfection here is preverbs with diacritics won't be matched.
        # todo: consider exhaustively match preverbs with diacritics

        for preverb in Wordform.objects.filter(
            Q(full_lc="IPV") | Q(pos="IPV"),
            Q(text=user_query) | Q(text=user_query + "-"),
        ):  # regarding the appending dash, see:
            # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
            # these are as_is analysis generated by xml_importer.py::generate_as_is_analysis
            lemmas_by_analysis[preverb.analysis].append(preverb)

        # Words/phrases with spaces in CW dictionary can not be analyzed by fst and are labeled "as_is".
        # However we do want to show them. We trust CW dictionary here and filter those lemmas that has any definition
        # that comes from CW

        # todo: remind user "are you searching in cree/english?"
        lemmas_by_english: List["Wordform"] = []
        if " " not in user_query:  # a whole word
            lemma_ids = EnglishKeyword.objects.filter(text__iexact=user_query).values(
                "lemma__id"
            )

            lemmas_by_english.extend(
                list(Wordform.objects.filter(id__in=lemma_ids, as_is=False))
            )

            # explain above, preverbs should be presented
            lemmas_by_english.extend(
                list(
                    Wordform.objects.filter(
                        Q(pos="IPV") | Q(full_lc="IPV") | Q(pos="PRON"),
                        id__in=lemma_ids,
                        as_is=True,
                    )
                )
            )

        return CreeAndEnglish(
            {analysis: set(lemmas) for analysis, lemmas in lemmas_by_analysis.items()},
            set(lemmas_by_english),
        )

    @staticmethod
    def search(user_query: str) -> Tuple[str, List[SearchResult]]:
        """
        Returns the matched language (as an ISO 639 code), and list of search
        results.
        """
        cree_results, english_results = Wordform.fetch_lemma_by_user_query(user_query)

        if len(cree_results) < len(english_results):
            raise NotImplementedError(
                "I don't know how to deal with English search results"
            )

        matched_wordforms: Set[EntryKey] = set()

        # First, let's add all matched analyses:
        for analysis in cree_results.keys():
            for entry in determine_entries_from_analysis(analysis):
                matched_wordforms.add(entry)

        results: List[SearchResult] = []

        # Create the search results
        for entry in matched_wordforms:
            try:
                lemma = Wordform.objects.get(text=entry.lemma, is_lemma=True)
            except Wordform.DoesNotExist:
                logging.warning(
                    "Could not find matching inflection for %r "
                    "searched from %r (results: %r)",
                    entry,
                    user_query,
                    cree_results,
                )
                continue

            definitions = tuple(Definition.objects.filter(lemma=lemma))
            if len(definitions) < 1:
                logging.warning(
                    "Could not find definitions for %r (lemma: %r)",
                    entry.wordform,
                    lemma,
                )
                continue

            results.append(
                SearchResult(
                    wordform=entry.wordform,
                    part_of_speech=lemma.full_lc,
                    is_lemma=entry.wordform == lemma.text,
                    lemma=lemma.text,
                    preverbs=(),  # type: ignore
                    reduplication_tags=(),  # type: ignore
                    initial_change_tags=(),  # type: ignore
                    definitions=definitions,  # type: ignore
                )
            )
            # fixme: Eddie: remove all these type ignores and let mypy shut up

        # TODO: sort them!

        return "crk", results


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

    # A definition defines a particular word form (usually a lemma)
    lemma = models.ForeignKey(Wordform, on_delete=models.CASCADE)

    # Why this property exists:
    # because DictionarySource should be its own model, but most code only
    # cares about the source IDs. So this removes the coupling to how sources
    # are stored and returns the source IDs right away.
    @property
    def source_ids(self):
        """
        A tuple of the source IDs that this definition cites.
        """
        return tuple(sorted(source.abbrv for source in self.citations.all()))

    def __str__(self):
        return self.text


class EnglishKeyword(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=20)

    lemma = models.ForeignKey(
        Wordform, on_delete=models.CASCADE, related_name="english_keyword"
    )

    class Meta:
        indexes = [models.Index(fields=["text"])]


################################## Helpers ##################################


def determine_entries_from_analysis(analysis: str):
    """
    Given a analysis, returns an entry.
    """
    result = fst_analysis_parser.extract_lemma_and_category(analysis)
    assert result is not None, f"Could not parse lemma and category from {analysis}"
    lemma, pos = result
    normatized_forms: List[Tuple[str]] = normative_generator.feed(analysis)
    for (wordform,) in normatized_forms:
        yield EntryKey(wordform, lemma, pos)
