import unicodedata
from functools import cmp_to_key, partial
from typing import Tuple, cast, Set, Iterable, List, Callable, Any, Optional

from cree_sro_syllabics import syllabics2sro
from sortedcontainers import SortedSet

from API.models import Wordform, Definition, get_all_source_ids_for_definition
from utils import Language, get_modified_distance
from utils.cree_lev_dist import remove_cree_diacritics
from utils.fst_analysis_parser import LABELS, partition_analysis
from utils.types import FSTTag, Label, ConcatAnalysis
from .ranking import sort_search_result
from .types import (
    InternalForm,
    Preverb,
    CreeAndEnglish,
    CreeResult,
    EnglishResult,
    SearchResult,
)


class _BaseWordformSearch:
    """
    Handles searching for one particular query.
    """

    def __init__(self, query: str):
        self.cleaned_query = to_internal_form(clean_query_text(query))

    def perform(self, include_auto_definitions) -> SortedSet[SearchResult]:
        """
        Do the search
        :return: sorted search results
        """

        res = self.fetch_bilingual_results()
        results = SortedSet(key=sort_by_user_query(self.cleaned_query))
        results |= self.prepare_cree_results(
            res.cree_results, include_auto_definitions=include_auto_definitions
        )
        results |= self.prepare_english_results(
            res.english_results, include_auto_definitions=include_auto_definitions
        )
        return results

    def fetch_bilingual_results(self) -> CreeAndEnglish:
        """
        Subclasses must implement this!
        """
        raise NotImplementedError

    def prepare_cree_results(
        self, cree_results: Set[CreeResult], include_auto_definitions: bool
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

            definitions = filter_auto_definitions(definitions, include_auto_definitions)

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
                raw_suffix_tags=tuple(linguistic_breakdown_tail),
                lemma_wordform=cree_result.lemma,
                preverbs=get_preverbs_from_head_breakdown(linguistic_breakdown_head),
                reduplication_tags=(),
                initial_change_tags=(),
                definitions=definitions,
            )

    def prepare_english_results(
        self, english_results: Set[EnglishResult], include_auto_definitions: bool
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
                raw_suffix_tags=tuple(linguistic_breakdown_tail),
                definitions=tuple(result.matched_cree.definitions.all()),
                # todo: current EnglishKeyword is bound to
                #       lemmas, whose definitions are guaranteed in the database.
                #       This may be an empty tuple in the future
                #       when EnglishKeyword can be associated with non-lemmas
            )


def to_internal_form(user_query: str) -> InternalForm:
    """
    Convert text to the internal form used by the database entries, tries, FSTs, etc.

    In itwêwina, the Plains Cree dictionary, this means SRO circumflexes.
    """
    return InternalForm(to_sro_circumflex(user_query))


def to_sro_circumflex(text: str) -> str:
    """
    Convert text to Plains Cree SRO with circumflexes (êîôâ).

    >>> to_sro_circumflex("tān'si")
    "tân'si"
    >>> to_sro_circumflex("ᑖᓂᓯ")
    'tânisi'
    """
    text = text.replace("ā", "â").replace("ē", "ê").replace("ī", "î").replace("ō", "ô")
    return syllabics2sro(text)


def replace_user_friendly_tags(fst_tags: List[FSTTag]) -> List[Label]:
    """ replace fst-tags to cute ones"""
    return LABELS.english.get_full_relabelling(fst_tags)


def clean_query_text(user_query: str) -> str:
    """
    Cleans up the query text before it is passed to further steps.
    """
    # Whitespace won't affect results, but the FST can't deal with it:
    user_query = user_query.strip()
    # All internal text should be in NFC form --
    # that is, all characters that can be composed are composed.
    user_query = unicodedata.normalize("NFC", user_query)
    return user_query.lower()


def safe_partition_analysis(analysis: ConcatAnalysis):
    try:
        (
            linguistic_breakdown_head,
            _,
            linguistic_breakdown_tail,
        ) = partition_analysis(analysis)
    except ValueError:
        linguistic_breakdown_head = []
        linguistic_breakdown_tail = []
    return linguistic_breakdown_head, linguistic_breakdown_tail


def sort_by_user_query(user_query: InternalForm) -> Callable[[Any], Any]:
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
                            normative_preverb_text,
                            pr.text.strip("-"),
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


def filter_auto_definitions(
    definitions: tuple[Definition, ...], include_auto_definitions: bool
) -> tuple[Definition, ...]:
    if include_auto_definitions:
        return definitions

    ret = []
    for d in definitions:
        if "auto" not in get_all_source_ids_for_definition(d.id):
            ret.append(d)
    return tuple(ret)
