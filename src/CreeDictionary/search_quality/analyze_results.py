# The analyses in this file don’t touch the database, and might perform some
# expensive operations, because they are meant for analyzing and comparing
# outputs generated today using the latest everything to previously-generated
# outputs using old versions of the code and old versions of the dictionary.

from __future__ import annotations

import gzip
from json import load
from os import PathLike
from typing import cast, TypedDict, Optional

from CreeDictionary.API.schema import SerializedSearchResult
from . import DEFAULT_SAMPLE_FILE, SampleSearchResultsJson
from .sample import load_sample_definition, SampleDefinition


class DuplicateInfo(TypedDict):
    total: int
    unique: int


class SingleQueryAnalysis(TypedDict, total=False):
    time_taken_seconds: float
    result_count: int
    total_duplicate_count: int
    unique_duplicate_count: int
    topthree_score_percent: float
    threeten_score_percent: float
    word_1: str
    word_1_rank: int | str
    word_2: str
    word_2_rank: int | str
    word_3: str
    word_3_rank: int | str


Analysis = dict[str, Optional[SingleQueryAnalysis]]


def count_results(results: list[SerializedSearchResult]):
    return sum(1 if r["is_lemma"] else 2 for r in results)


class PartialSerializedWordform(TypedDict, total=False):
    text: str
    inflectional_category: str


class DuplicateAnnotatedSearchResult(TypedDict, total=False):
    """Related to SerializedSearchResult

    Without the equivalent of TypeScript’s Pick<> and other conditional/utility
    types (https://www.typescriptlang.org/docs/handbook/utility-types.html), we
    manually approximate the relation.
    """

    wordform_text: Optional[str]
    # legacy, deprecated
    matched_cree: Optional[str]

    lemma_wordform: PartialSerializedWordform
    is_duplicate_of: Optional[str]


def get_result_text(r: DuplicateAnnotatedSearchResult | SerializedSearchResult):
    # Use the new language-independent key if available
    if "wordform_text" in r:
        return r["wordform_text"]
    # Fall back to old thing
    return r["matched_cree"]


def count_and_annotate_dupes(
    results: list[SerializedSearchResult],
) -> DuplicateInfo:
    """Count duplicate results, MUTATING them to add descriptive annotations

    A string key "is_duplicate_of" is added to aid finding the duplicate entries
    in the JSON.

    Returns (# of duplicate results, # of unique duplicates)
    e.g., ['cat', 'cat', 'dog', 'dog', 'dog', 'horse'] would return (3, 2)
    """

    dupllcate_results = 0
    unique_duplicates = set()
    seen: dict[str, DuplicateAnnotatedSearchResult] = {}

    for r_ in results:
        r = cast(DuplicateAnnotatedSearchResult, r_)
        normalized = "\n".join(
            [
                get_result_text(r),
                r["lemma_wordform"]["text"],
                r["lemma_wordform"]["inflectional_category"],
            ]
        )
        if normalized in seen:
            dupllcate_results += 1

            seen[normalized]["is_duplicate_of"] = f"first {normalized}"
            r["is_duplicate_of"] = normalized

            if normalized not in unique_duplicates:
                unique_duplicates.add(normalized)

        else:
            seen[normalized] = r

    return {"total": dupllcate_results, "unique": len(unique_duplicates)}


def find_rank(word: str, results: list[SerializedSearchResult]):
    if not word.strip():
        return ""  # n/a

    index = 1
    for r in results:
        # We also have the definition here, could include it
        if word == get_result_text(r):
            return index
        index += 1 if r["is_lemma"] else 2
    return "☹"


def load_results_file(results_file: PathLike) -> SampleSearchResultsJson:
    with gzip.open(results_file, "rb") as f:
        search_results: SampleSearchResultsJson = load(f)
        return search_results


def analyze(results_file, sample_definition: SampleDefinition = None):
    """

    If sample_definition is None, the default will be used.
    """

    if sample_definition is None:
        sample_definition = load_sample_definition(DEFAULT_SAMPLE_FILE)

    search_results = load_results_file(results_file)

    analysis: Analysis = {}

    for row in sample_definition:
        keyword = row["Query"]

        keyword_search_results = search_results.get(keyword, None)

        if keyword_search_results is None:
            analysis[keyword] = None
            continue

        result_list = keyword_search_results["results"]

        dupe_info = count_and_annotate_dupes(result_list)

        query_analysis: SingleQueryAnalysis = {
            "time_taken_seconds": keyword_search_results["time_taken_seconds"],
            "result_count": count_results(result_list),
            "total_duplicate_count": dupe_info["total"],
            "unique_duplicate_count": dupe_info["unique"],
        }

        # How many top expected results does the sample specify for this
        # query?
        specified_result_count = 0
        result_found_count = 0
        threeten_good_result_count = 0

        for i in (1, 2, 3):
            # mypy does not like dynamic keys
            word = cast(dict, row)[f"Nêhiyawêwin_{i}"]

            if not word:
                continue

            cast(dict, query_analysis)[f"word_{i}"] = word
            rank = find_rank(word, result_list)
            cast(dict, query_analysis)[f"word_{i}_rank"] = rank

            specified_result_count += 1
            if isinstance(rank, int):
                result_found_count += 1

                if rank < 10:
                    threeten_good_result_count += 1

        query_analysis["topthree_score_percent"] = (
            100 * result_found_count / specified_result_count
        )
        query_analysis["threeten_score_percent"] = (
            100 * threeten_good_result_count / specified_result_count
        )

        analysis[keyword] = query_analysis

    return analysis
