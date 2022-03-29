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
            # The POS and corp-freq coefficients have been overriden to be the same on purpose
            0.0244343126
            + -0.0004337761 * result.wordform_length
            + 0.0378554865 * len(result.target_language_keyword_match)
            # + -2.094435278e-17 * _has_value(result.morpheme_ranking)
            + 0.0244343126 * _default_if_none(result.morpheme_ranking, default=1)
            + 0.0036 * _default_if_none(result.is_espt_result, default=0)
            + 0.0447407131 * _default_if_none(result.pos_match, default=0)
            + 0.0447407131 * _default_if_none(result.word_list_freq, default=0)
            + 0.0000122003 * _default_if_none(result.lemma_freq, default=0)
            + -0.0693265378
            * log(1 + _default_if_none(result.cosine_vector_distance, default=1.1))
        )
