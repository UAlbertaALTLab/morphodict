import pytest
from pytest import approx

from CreeDictionary.API.search import search
from CreeDictionary.API.search.ranking import assign_relevance_score
from CreeDictionary.API.search.types import Result
from morphodict.lexicon.models import Wordform


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
@pytest.mark.skip()
@pytest.mark.parametrize(
    ("expected", "kwargs"),
    [
        # Simple tests that use increasingly many parameters.
        (0.012_082, {"cosine_vector_distance": 0.7}),
        (0.285_758, {"morpheme_ranking": 12.8}),
        (0.300_407, {"cosine_vector_distance": 0.7, "morpheme_ranking": 12.8}),
        # A real-world relevance score from a sample query.
        (
            0.464_090,
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


@pytest.mark.skip()
def test_cvd_exclusive_only_uses_cvd_for_ranking(db):
    search_run = search(query="dance cvd:2")
    results = search_run.sorted_results()
    assert len(results) > 2

    def is_sorted_by_cvd(results: list[Result]):
        for r1, r2 in zip(results, results[1:]):
            if (
                r1.cosine_vector_distance is not None
                and r2.cosine_vector_distance is not None
                and r1.cosine_vector_distance > r2.cosine_vector_distance
            ):
                raise Exception(f"Item {r1} comes first but has a bigger cvd than {r2}")
        return True

    assert is_sorted_by_cvd(results)
