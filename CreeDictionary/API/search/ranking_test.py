import pytest
from pytest import approx

from API.models import Wordform
from API.search.ranking import assign_relevance_score
from API.search.types import Result


def build_result(
    wordform_length=0,
    target_language_keyword_match_len=0,
    **result_kwargs,
):
    wf = Wordform(text="f" * wordform_length, is_lemma=True)
    wf.lemma = wf

    result_kwargs.setdefault(
        "target_language_keyword_match", ["x"] * target_language_keyword_match_len
    )
    result = Result(wf, **result_kwargs)
    return result


@pytest.mark.parametrize(
    ("expected", "kwargs"),
    [
        (-0.033_454, {"did_match_target_language": True}),
        (-0.008_289, {"cosine_vector_distance": 0.7}),
        (-0.022_457, {"morpheme_ranking": 12.8}),
        (0.002_708, {"cosine_vector_distance": 0.7, "morpheme_ranking": 12.8}),
        (
            0.062_559,
            {
                "wordform_length": 9,
                "target_language_keyword_match_len": 1,
                "cosine_vector_distance": 0.248058,
                "morpheme_ranking": 17.2326,
            },
        ),
    ],
)
def test_model_evaluation(expected, kwargs):
    result = build_result(**kwargs)
    assign_relevance_score(result)
    assert result.relevance_score == approx(expected, abs=1e-6)
