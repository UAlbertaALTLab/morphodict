from morphodict.search import wordnet_search
from morphodict.search.types import Result


def test_wordnet_fail(db):
    search_results = wordnet_search(query="failingsearchinwordnet wn:1")
    assert search_results is None


def test_wordnet_empty(db):
    search_results = wordnet_search(query="wn:1")
    assert search_results is None


def test_wordnet_success(db):
    search_results = wordnet_search(query="see wn:1")

    assert len(search_results) > 1
    for wn_entry, results in search_results:
        assert len(results.sorted_results()) > 0


def test_wordnet_space_success(db):
    search_results = wordnet_search(query="Ursa Major wn:1")

    assert len(search_results) > 0
    for wn_entry, results in search_results:
        assert len(results.sorted_results()) > 0
