from __future__ import annotations

from functools import cmp_to_key, partial
from math import log
from typing import Callable, Any, cast

from utils import get_modified_distance
from . import core
from .types import Result
from ..models import wordform_cache, Wordform


def sort_search_result(
    res_a: Result,
    res_b: Result,
    search_run: core.SearchRun,
) -> float:
    """
    determine how we sort search results.

    :return:   0: does not matter;
              >0: res_a should appear after res_b;
              <0: res_a should appear before res_b.
    """

    if res_a.did_match_source_language and res_b.did_match_source_language:
        # both from source
        a_dis = get_modified_distance(search_run.internal_query, res_a.wordform.text)
        b_dis = get_modified_distance(search_run.internal_query, res_b.wordform.text)
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
    elif res_a.did_match_source_language:
        # a from source, b from target
        return -1
    elif res_b.did_match_target_language:
        # a from target, b from source
        return 1
    else:
        # both from English
        if (
            res_a.cosine_vector_distance is not None
            and res_b.cosine_vector_distance is not None
        ):
            return res_a.cosine_vector_distance - res_b.cosine_vector_distance

        a_in_rankings = res_a.wordform.text in wordform_cache.MORPHEME_RANKINGS
        b_in_rankings = res_b.wordform.text in wordform_cache.MORPHEME_RANKINGS

        if a_in_rankings and not b_in_rankings:
            return -1
        elif not a_in_rankings and b_in_rankings:
            return 1
        elif not a_in_rankings and not b_in_rankings:
            return 0
        else:  # both in rankings
            return (
                wordform_cache.MORPHEME_RANKINGS[res_a.wordform.text]
                - wordform_cache.MORPHEME_RANKINGS[res_b.wordform.text]
            )


def sort_by_user_query(search_run: core.SearchRun) -> Callable[[Any], Any]:
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
            partial(sort_search_result, search_run=search_run),
        )
    )


def _has_value(value):
    if value is None:
        return 0
    return 1


def _default_if_none(value, *, default):
    if value is not None:
        return value
    return default


def assign_relevance_score(result: Result):
    # Until we have some training data for Cree queries, we keep the intent of
    # the old sort order:
    #   - Cree wordforms in the query take precedence over any English hits
    #   - Then use edit distance
    #   - Finally, prefer lemmas
    if result.did_match_source_language:
        result.relevance_score = (
            1000
            - 20 * _default_if_none(result.query_wordform_edit_distance, default=0)
            - _default_if_none(result.morpheme_ranking, default=20)
            + (1 if result.is_lemma else 0)
        )
    else:
        result.relevance_score = (
            # See weighting.ipynb for the model that produced these coefficients.
            0.05537813
            + -0.00056731 * result.wordform_length
            + 0.03264485 * len(result.target_language_keyword_match)
            + 0.023535 * _has_value(result.morpheme_ranking)
            + -0.00099665 * _default_if_none(result.morpheme_ranking, default=0)
            + -0.11957764
            * log(1 + _default_if_none(result.cosine_vector_distance, default=1.1))
        )


def test_model_evaluation():
    from pytest import approx

    wf = Wordform(text="f", is_lemma=True)
    wf.lemma = wf

    result = Result(wf, did_match_target_language=True)
    assign_relevance_score(result)
    assert result.relevance_score == approx(-0.033908, abs=1e-6)

    result = Result(wf, cosine_vector_distance=0.7)
    assign_relevance_score(result)
    assert result.relevance_score == approx(-0.00864, abs=1e-6)

    result = Result(wf, morpheme_ranking=12.8)
    assign_relevance_score(result)
    assert result.relevance_score == approx(-0.023130453155353087, abs=1e-6)

    result = Result(wf, cosine_vector_distance=0.7, morpheme_ranking=12.8)
    assign_relevance_score(result)
    assert result.relevance_score == approx(0.002137, abs=1e-6)

    wf.text = "x" * 11
    result = Result(
        wf,
        cosine_vector_distance=0.0,
        morpheme_ranking=15.39,
        target_language_keyword_match=["x", "x"],
    )
    assign_relevance_score(result)
    assert result.relevance_score == approx(0.122624, abs=1e-6)
