#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from functools import cmp_to_key, partial
from typing import List, Callable, Any, cast, NewType

from utils import Language, get_modified_distance

from utils.fst_analysis_parser import LABELS, partition_analysis
from utils.types import FSTTag, Label, ConcatAnalysis

import logging
import unicodedata
from itertools import chain
from typing import (
    Iterable,
    List,
    NamedTuple,
    NewType,
    Optional,
    Set,
    Tuple,
    Union,
    cast
)

import attr
from attr import attrs
from cree_sro_syllabics import syllabics2sro
from django.conf import settings
from django.db.models import Q
from sortedcontainers import SortedSet

from CreeDictionary import hfstol as temp_hfstol
from utils import Language, PartOfSpeech, fst_analysis_parser, get_modified_distance
from utils.cree_lev_dist import remove_cree_diacritics
from utils.english_keyword_extraction import stem_keywords
from utils.fst_analysis_parser import LABELS
from utils.types import ConcatAnalysis, FSTTag

from .models import Definition, EnglishKeyword, Wordform
from .schema import SerializedSearchResult
from .utils import SortedSetWithExtend

# it's a str when the preverb does not exist in the database
Preverb = Union[Wordform, str]
Lemma = NewType("Lemma", Wordform)
MatchedEnglish = NewType("MatchedEnglish", str)


logger = logging.getLogger(__name__)


@attrs(auto_attribs=True, frozen=True)  # frozen makes it hashable
class SearchResult:
    """
    Contains all of the information needed to display a search result.

    Comment:
    Each instance corresponds visually to one card shown on the interface
    """

    # the text of the match
    matched_cree: str

    is_lemma: bool

    # English or Cree
    matched_by: Language

    # The matched lemma
    lemma_wordform: Wordform

    # triple dots in type annotation means they can be empty

    # user friendly linguistic breakdowns
    linguistic_breakdown_head: Tuple[str, ...]
    linguistic_breakdown_tail: Tuple[str, ...]

    # Sequence of all preverb tags, in order
    # Optional: we might not have some preverbs in our database
    preverbs: Tuple[Preverb, ...]

    # TODO: there are things to be figured out for this :/
    # Sequence of all reduplication tags present, in order
    reduplication_tags: Tuple[str, ...]
    # Sequence of all initial change tags
    initial_change_tags: Tuple[str, ...]

    definitions: Tuple[Definition, ...]

    def serialize(self) -> SerializedSearchResult:
        """
        serialize the instance, can be used before passing into a template / in an API view, etc.
        """
        # note: passing in serialized "dumb" object instead of smart ones to templates is a Django best practice
        # it avoids unnecessary database access and makes APIs easier to create
        result = attr.asdict(self)
        # lemma field will refer to lemma_wordform itself, which makes it impossible to serialize
        result["lemma_wordform"] = self.lemma_wordform.serialize()

        result["preverbs"] = []
        for pv in self.preverbs:
            if isinstance(pv, str):
                result["preverbs"].append(pv)
            else:  # Wordform
                result["preverbs"].append(pv.serialize())

        result["matched_by"] = self.matched_by.name
        result["definitions"] = [
            definition.serialize() for definition in self.definitions
        ]
        return cast(SerializedSearchResult, result)


class CreeResult(NamedTuple):
    """
    - analysis: a string, fst analysis of normatized cree

    - normatized_cree: a wordform, the Cree inflection that matches the analysis
        Can be a string that's not saved in the database since our database do not store all the
        weird inflections

    - lemma: a Wordform object, the lemma of the matched inflection
    """

    analysis: ConcatAnalysis
    normatized_cree: Union[Wordform, str]
    lemma: Lemma

    @property
    def normatized_cree_text(self) -> str:
        if isinstance(self.normatized_cree, Wordform):
            return self.normatized_cree.text
        else:  # is str
            return self.normatized_cree


class EnglishResult(NamedTuple):
    """
    - matched_english: a string, the English that matches user query, currently it will just be the same as user query.
        (unicode normalized, lowercased)

    - normatized_cree: a string, the Cree inflection that matches the English

    - lemma: a Wordform object, the lemma of the matched inflection
    """

    matched_english: MatchedEnglish
    matched_cree: Wordform
    lemma: Lemma


class CreeAndEnglish(NamedTuple):
    """
    Duct tapes together two kinds of search results:

     - cree results -- an ordered set of CreeResults, should be sorted by the modified levenshtein distance between the
        analysis and the matched normatized form
     - english results -- an ordered set of EnglishResults, sorting mechanism is to be determined
    """

    # MatchedCree are inflections
    cree_results: Set[CreeResult]
    english_results: Set[EnglishResult]


class WordformSearch:
    """
    Intermediate class while I'm figuring out this refactor :/
    """

    def __init__(self, query: str, constraints: dict):
        self.query = query
        self.constraints = constraints

    def perform(self) -> SortedSet[SearchResult]:
        """
        Do the search
        :return: sorted search results
        """
        res = fetch_lemma_by_user_query(self.query, **self.constraints)
        results = SortedSetWithExtend(key=sort_by_user_query(self.query))
        results.extend(self.prepare_cree_results(res.cree_results))
        results.extend(self.prepare_english_results(res.english_results))
        return results

    def prepare_cree_results(
        self, cree_results: Set[CreeResult]
    ) -> Iterable[SearchResult]:
        # Create the search results
        for cree_result in cree_results:
            matched_cree = cree_result.normatized_cree_text
            if isinstance(cree_result.normatized_cree, Wordform):
                is_lemma = cree_result.normatized_cree.is_lemma
                definitions = tuple(cree_result.normatized_cree.definitions.all())
            else:
                is_lemma = False
                definitions = ()

            (
                linguistic_breakdown_head,
                linguistic_breakdown_tail,
            ) = safe_partition_analysis(cree_result.analysis)

            # todo: tags
            yield SearchResult(
                matched_cree=matched_cree,
                is_lemma=is_lemma,
                matched_by=Language.CREE,
                linguistic_breakdown_head=tuple(
                    replace_user_friendly_tags(linguistic_breakdown_head)
                ),
                linguistic_breakdown_tail=tuple(
                    replace_user_friendly_tags(linguistic_breakdown_tail)
                ),
                lemma_wordform=cree_result.lemma,
                preverbs=get_preverbs_from_head_breakdown(linguistic_breakdown_head),
                reduplication_tags=(),
                initial_change_tags=(),
                definitions=definitions,
            )

    def prepare_english_results(
        self, english_results: Set[EnglishResult]
    ) -> Iterable[SearchResult]:
        for result in english_results:
            (
                linguistic_breakdown_head,
                linguistic_breakdown_tail,
            ) = safe_partition_analysis(result.lemma.analysis)

            yield SearchResult(
                matched_cree=result.matched_cree.text,
                is_lemma=result.matched_cree.is_lemma,
                matched_by=Language.ENGLISH,
                lemma_wordform=result.matched_cree.lemma,
                preverbs=get_preverbs_from_head_breakdown(linguistic_breakdown_head),
                reduplication_tags=(),
                initial_change_tags=(),
                linguistic_breakdown_head=tuple(
                    replace_user_friendly_tags(linguistic_breakdown_head)
                ),
                linguistic_breakdown_tail=tuple(
                    replace_user_friendly_tags(linguistic_breakdown_tail)
                ),
                definitions=tuple(result.matched_cree.definitions.all()),
                # todo: current EnglishKeyword is bound to
                #       lemmas, whose definitions are guaranteed in the database.
                #       This may be an empty tuple in the future
                #       when EnglishKeyword can be associated with non-lemmas
            )


def filter_cw_wordforms(q: Iterable[Wordform]) -> Iterable[Wordform]:
    """
    return the wordforms that has definition from CW dictionary

    :param q: an Iterable of Wordforms
    """
    for wordform in q:
        for definition in wordform.definitions.all():
            if "CW" in definition.source_ids:
                yield wordform
                break


def get_preverbs_from_head_breakdown(
    head_breakdown: List[FSTTag],
) -> Tuple[Preverb, ...]:
    results = []

    for tag in head_breakdown:
        preverb_result: Optional[Preverb] = None
        if tag.startswith("PV/"):
            # use altlabel.tsv to figure out the preverb

            # ling_short looks like: "Preverb: âpihci-"
            ling_short = LABELS.linguistic_short.get(tag)
            if ling_short is not None and ling_short != "":
                # looks like: "âpihci"
                normative_preverb_text = ling_short[len("Preverb: ") : -1]
                preverb_results = fetch_preverbs(normative_preverb_text)

                # find the one that looks the most similar
                if preverb_results:
                    preverb_result = min(
                        preverb_results,
                        key=lambda pr: get_modified_distance(
                            normative_preverb_text, pr.text.strip("-"),
                        ),
                    )

                else:  # can't find a match for the preverb in the database
                    preverb_result = normative_preverb_text

        if preverb_result is not None:
            results.append(preverb_result)
    return tuple(results)


def fetch_preverbs(user_query: str) -> Set[Wordform]:
    """
    Search for preverbs in the database by matching the circumflex-stripped forms. MD only contents are filtered out.
    trailing dash relaxation is used

    :param user_query: unicode normalized, to_lower-ed
    """

    if user_query.endswith("-"):
        user_query = user_query[:-1]
    user_query = remove_cree_diacritics(user_query)

    return Wordform.PREVERB_ASCII_LOOKUP[user_query]


def fetch_lemma_by_user_query(user_query: str, **extra_constraints) -> CreeAndEnglish:
    """
    treat the user query as cree and:

    Give the analysis of user query and matched lemmas.
    There can be multiple analysis for user queries
    One analysis could match multiple lemmas as well due to underspecified database fields.
    (inflectional_category and pos can be empty)

    treat the user query as English keyword and:

    Give a list of matched lemmas

    :param user_query: can be English or Cree (syllabics or not)
    :param extra_constraints: additional fields to disambiguate
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
    # 1. affix search (return all results that ends/starts with the query string)
    # 2. spell relax in descriptive fst
    # 2. definition containment of the query word

    cree_results: Set[CreeResult] = set()

    # there will be too many matches for some shorter queries
    if len(user_query) > settings.AFFIX_SEARCH_THRESHOLD:
        # prefix and suffix search
        ids_by_prefix = Wordform.affix_searcher.search_by_prefix(user_query)
        ids_by_suffix = Wordform.affix_searcher.search_by_suffix(user_query)

        for wf in Wordform.objects.filter(
            id__in=set(chain(ids_by_prefix, ids_by_suffix)), **extra_constraints
        ):
            cree_results.add(CreeResult(wf.analysis, wf, wf.lemma))

    # utilize the spell relax in descriptive_analyzer
    # TODO: use shared.descriptive_analyzer (HFSTOL) when this bug is fixed:
    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    fst_analyses: Set[ConcatAnalysis] = set(
        a.concatenate() for a in temp_hfstol.analyze(user_query)
    )

    all_standard_forms = []

    for analysis in fst_analyses:
        # todo: test

        exactly_matched_wordforms = Wordform.objects.filter(
            analysis=analysis, as_is=False, **extra_constraints
        )

        if exactly_matched_wordforms.exists():
            for wf in exactly_matched_wordforms:
                cree_results.add(
                    CreeResult(ConcatAnalysis(wf.analysis), wf, Lemma(wf.lemma))
                )
        else:
            # When the user query is outside of paradigm tables
            # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
            # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+3Sg'}
            # e.g. Err/Orth: ewapamat: {'PV/e+wâpamêw+V+TA+Cnj+3Sg+4Sg/PlO+Err/Orth'

            lemma_wc = fst_analysis_parser.extract_lemma_text_and_word_class(analysis)
            if lemma_wc is None:
                logger.error(
                    f"fst_analysis_parser cannot understand analysis {analysis}"
                )
                continue

            # now we generate the standardized form of the user query for display purpose
            # notice Err/Orth tags needs to be stripped because it makes our generator generate un-normatized forms
            normatized_form_for_analysis = [
                *temp_hfstol.generate(
                    analysis.replace("+Err/Orth", "").replace("+Err/Frag", "")
                )
            ]
            all_standard_forms.extend(normatized_form_for_analysis)
            if len(all_standard_forms) == 0:
                logger.error(
                    f"can not generate standardized form for analysis {analysis}"
                )
            normatized_user_query = min(
                normatized_form_for_analysis,
                key=lambda f: get_modified_distance(f, user_query),
            )

            lemma, word_class = lemma_wc
            matched_lemma_wordforms = Wordform.objects.filter(
                text=lemma, is_lemma=True, **extra_constraints
            )

            # now we get wordform objects from database
            # Note:
            # non-analyzable matches should not be displayed (mostly from MD)
            # like "nipa", which means kill him
            # those results are filtered out by `as_is=False` below
            # suggested by Arok Wolvengrey

            if word_class.pos is PartOfSpeech.PRON:
                # specially handle pronouns.
                # this is a temporary fix, otherwise "ôma" won't appear in the search results, since
                # "ôma" has multiple analysis
                # ôma+Ipc+Foc
                # ôma+Pron+Dem+Prox+I+Sg
                # ôma+Pron+Def+Prox+I+Sg
                # it's ambiguous which one is the lemma in the importing process thus it's labeled "as_is"

                # a more permanent fix requires every pronouns lemma to be listed and specified
                for lemma_wordform in matched_lemma_wordforms:
                    cree_results.add(
                        CreeResult(
                            ConcatAnalysis(analysis.replace("+Err/Orth", "")),
                            normatized_user_query,
                            Lemma(lemma_wordform),
                        )
                    )
            else:
                for lemma_wordform in matched_lemma_wordforms.filter(
                    as_is=False, pos=word_class.pos.name, **extra_constraints
                ):
                    cree_results.add(
                        CreeResult(
                            ConcatAnalysis(analysis.replace("+Err/Orth", "")),
                            normatized_user_query,
                            Lemma(lemma_wordform),
                        )
                    )

    # we choose to trust CW and show those matches with definition from CW.
    # text__in = all_standard_forms help match those lemmas that are labeled as_is but trust-worthy nonetheless
    # because they come from CW
    # text__in = [user_query] help matching entries with spaces in it, which fst can't analyze.
    for cw_as_is_wordform in filter_cw_wordforms(
        Wordform.objects.filter(
            text__in=all_standard_forms + [user_query],
            as_is=True,
            is_lemma=True,
            **extra_constraints,
        )
    ):
        cree_results.add(
            CreeResult(
                ConcatAnalysis(cw_as_is_wordform.analysis),
                cw_as_is_wordform,
                Lemma(cw_as_is_wordform),
            )
        )

    # as per https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
    # preverbs should be presented
    # exhaustively search preverbs here (since we can't use fst on preverbs.)

    for preverb_wf in fetch_preverbs(user_query):
        cree_results.add(
            CreeResult(
                ConcatAnalysis(preverb_wf.analysis), preverb_wf, Lemma(preverb_wf),
            )
        )

    # Words/phrases with spaces in CW dictionary can not be analyzed by fst and are labeled "as_is".
    # However we do want to show them. We trust CW dictionary here and filter those lemmas that has any definition
    # that comes from CW

    # now we get results searched by English
    # todo: remind user "are you searching in cree/english?"
    # todo: allow inflected forms to be searched through English. (requires database migration
    #  since now EnglishKeywords are bound to lemmas)
    english_results: Set[EnglishResult] = set()
    for stemmed_keyword in stem_keywords(user_query):

        lemma_ids = EnglishKeyword.objects.filter(
            text__iexact=stemmed_keyword, **extra_constraints
        ).values("lemma__id")

        for wordform in Wordform.objects.filter(id__in=lemma_ids, **extra_constraints):
            english_results.add(
                EnglishResult(MatchedEnglish(user_query), wordform, Lemma(wordform))
            )  # will become  (user_query, inflection.text, inflection.lemma)

        # explained above, preverbs should be presented
        for wordform in Wordform.objects.filter(
            Q(pos="IPV") | Q(inflectional_category="IPV") | Q(pos="PRON"),
            id__in=lemma_ids,
            as_is=True,
            **extra_constraints,
        ):
            english_results.add(
                EnglishResult(MatchedEnglish(user_query), wordform, Lemma(wordform))
            )  # will become  (user_query, inflection.text, wordform)

    return CreeAndEnglish(cree_results, english_results)




def replace_user_friendly_tags(fst_tags: List[FSTTag]) -> List[Label]:
    """ replace fst-tags to cute ones"""
    return LABELS.english.get_full_relabelling(fst_tags)


def safe_partition_analysis(analysis: ConcatAnalysis):
    try:
        (linguistic_breakdown_head, _, linguistic_breakdown_tail,) = partition_analysis(
            analysis
        )
    except ValueError:
        linguistic_breakdown_head = []
        linguistic_breakdown_tail = []
    return linguistic_breakdown_head, linguistic_breakdown_tail


def sort_search_result(
        res_a: "SearchResult", res_b: "SearchResult", user_query: str
) -> float:
    """
    determine how we sort search results.

    :return:   0: does not matter;
              >0: res_a should appear after res_b;
              <0: res_a should appear before res_b.
    """

    if res_a.matched_by is Language.CREE and res_b.matched_by is Language.CREE:
        # both from cree
        a_dis = get_modified_distance(user_query, res_a.matched_cree)
        b_dis = get_modified_distance(user_query, res_b.matched_cree)
        difference = a_dis - b_dis
        if difference:
            return difference

        # Both results are EXACTLY the same form!
        # Further disambiguate by checking if one is the lemma.
        if res_a.is_lemma and res_b.is_lemma:
            return 0
        elif res_a.is_lemma:
            return -1
        elif res_b.is_lemma:
            return 1
        else:
            # Somehow, both forms exactly match the user query and neither
            # is a lemma?
            return 0

    # todo: better English sort
    elif res_a.matched_by is Language.CREE:
        # a from cree, b from English
        return -1
    elif res_b.matched_by is Language.CREE:
        # a from English, b from Cree
        return 1
    else:
        from .models import Wordform

        # both from English
        a_in_rankings = res_a.matched_cree in Wordform.MORPHEME_RANKINGS
        b_in_rankings = res_b.matched_cree in Wordform.MORPHEME_RANKINGS

        if a_in_rankings and not b_in_rankings:
            return -1
        elif not a_in_rankings and b_in_rankings:
            return 1
        elif not a_in_rankings and not b_in_rankings:
            return 0
        else:  # both in rankings
            return (
                    Wordform.MORPHEME_RANKINGS[res_a.matched_cree]
                    - Wordform.MORPHEME_RANKINGS[res_b.matched_cree]
            )


def sort_by_user_query(user_query: str) -> Callable[[Any], Any]:
    """
    Returns a key function that sorts search results ranked by their distance
    to the user query.
    """
    # mypy doesn't really know how to handle partial(), so we tell it the
    # correct type with cast()
    # See: https://github.com/python/mypy/issues/1484
    return cmp_to_key(
        cast(
            Callable[[Any, Any], Any],
            partial(sort_search_result, user_query=user_query),
        )
    )
