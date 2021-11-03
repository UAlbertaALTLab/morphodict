from __future__ import annotations

from math import log

from . import types


def _has_value(value):
    if value is None:
        return 0
    return 1


def _default_if_none(value, *, default):
    if value is not None:
        return value
    return default


def assign_relevance_score(result: types.Result):
    # Until we have some training data for Cree queries, we keep the intent of
    # the old sort order:
    #   - Cree wordforms in the query take precedence over any English hits
    #   - Then use edit distance
    #   - Finally, prefer lemmas
    # The coefficients here are wild guesses that should accomplish that. They
    # can be replaced with computed values when we have some training data for
    # Cree-language queries.
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
            # The ESPT coefficient has been added at random for now--further investigation is needed
            0.0559011609
            + -0.0005685605 * result.wordform_length
            + 0.0325909057 * len(result.target_language_keyword_match)
            + 0.022778805 * _has_value(result.morpheme_ranking)
            + -0.0009984537 * _default_if_none(result.morpheme_ranking, default=1)
            + 0.0036 * _default_if_none(result.is_espt_result, default=0)
            + -0.1190890019
            * log(1 + _default_if_none(result.cosine_vector_distance, default=1.1))
        )
