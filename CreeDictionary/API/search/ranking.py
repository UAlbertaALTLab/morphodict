from __future__ import annotations

from math import log

from .types import Result
from ..models import Wordform


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
