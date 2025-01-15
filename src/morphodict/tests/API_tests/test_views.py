import pytest
import json
from django.urls import reverse

ASCII_WAPAMEW = "wapamew"
EXPECTED_SUFFIX_SEARCH_RESULT = "asawâpamêw"


@pytest.mark.django_db
@pytest.mark.skip(
    reason="Cannot use dictionary source and auto translations for click-in-text"
)
def test_click_in_text_correct_usage(client):
    # niskak means goose in plains Cree
    response = client.get(reverse("dictionary-word-click-in-text-api") + "?q=niskak")

    assert b"goose" in response.content


@pytest.mark.django_db
def test_click_in_text_no_params(client):
    response = client.get(reverse("dictionary-word-click-in-text-api"))

    assert response.status_code == 400


@pytest.mark.django_db
def test_normal_search_uses_affix_search(client):
    """
    Regular dictionary search should return affix results.

    e.g.,

    > search?q=wapamew
    should return both "wâpamêw" and "asawâpamêw"
    """
    normal_search_response = client.get(
        reverse("dictionary-search") + f"?q={ASCII_WAPAMEW}"
    ).content.decode("utf-8")
    assert EXPECTED_SUFFIX_SEARCH_RESULT in normal_search_response


@pytest.mark.django_db
def test_click_in_text_disables_affix_search(client):
    """
    The Click-in-Text API should NOT return affix results — too many results!

    e.g.,

    > search?q=wapamew
    should return "wâpamêw" but NOT "asawâpamêw"
    """
    click_in_text_response = client.get(
        reverse("dictionary-word-click-in-text-api") + f"?q={ASCII_WAPAMEW}"
    ).content.decode("utf-8")
    assert EXPECTED_SUFFIX_SEARCH_RESULT not in click_in_text_response


@pytest.mark.django_db
def test_dictionary_rapidword_index_api_fail(client):
    response = client.get(reverse("dictionary-rapidwords-index-api"))

    assert response.status_code == 400


@pytest.mark.django_db
def test_dictionary_rapidword_index_api_succeed(client):
    normal_search_response = client.get(
        reverse("dictionary-rapidwords-index-api") + f"?rw_index=5.2.2"
    ).content.decode("utf-8")
    json_response = json.loads(normal_search_response)
    assert "results" in json_response.keys()
    assert len(json_response["results"]) > 0
    for result in json_response["results"]:
        keys = result.keys()
        assert "lemma_wordform" in keys
        keys = result["lemma_wordform"].keys()
        assert "text" in keys
        assert "linguist_info" in keys
        assert "definitions" in keys
        for d in result["lemma_wordform"]["definitions"]:
            assert "text" in d.keys()
