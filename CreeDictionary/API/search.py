#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from typing import Tuple, cast, Iterable, List, Optional, Union, Set, NamedTuple

import attr
from API.models import Wordform, Lemma
from API.result_utils import MatchedEnglish
from attr import attrs

from API.schema import SerializedSearchResult
from utils import Language, get_modified_distance
from utils.cree_lev_dist import remove_cree_diacritics
from utils.fst_analysis_parser import LABELS
from utils.types import FSTTag, ConcatAnalysis

from .models import Wordform, Definition

Preverb = Union[Wordform, str]


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
