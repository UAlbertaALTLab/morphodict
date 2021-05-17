import pytest
from pytest import approx

from CreeDictionary.API.models import Wordform
from CreeDictionary.API.search.ranking import assign_relevance_score
from CreeDictionary.API.search.types import Result


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


# These tests help ensure we have implemented the same model as what’s in the
# jupyter notebook. At the time, copying the parameters seemed like the better
# thing going forward than pickling the model and adding a dependency, in terms
# of both maintainability and making sure the model is doing exactly what we
# think it is.
#
# They will need to be updated if the model parameters change.
@pytest.mark.parametrize(
    ("expected", "kwargs"),
    [
        # Simple tests that use increasingly many parameters.
        (-0.033_454, {"did_match_target_language": True}),
        (-0.008_289, {"cosine_vector_distance": 0.7}),
        (-0.022_457, {"morpheme_ranking": 12.8}),
        (0.002_708, {"cosine_vector_distance": 0.7, "morpheme_ranking": 12.8}),
        # A real-world relevance score from a sample query.
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
