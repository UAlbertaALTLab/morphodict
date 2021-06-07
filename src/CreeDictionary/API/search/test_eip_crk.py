from CreeDictionary.API.models import Wordform
from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.API.search.eip import EipSearch
from CreeDictionary.API.search.types import Result


def test_eip_search(db):
    search_run = SearchRun("they crawled")
    eip_search = EipSearch(search_run)
    eip_search.analyze_query()
    assert search_run.query.query_string == "crawls"
    assert search_run.query.query_terms == ["crawls"]
    assert eip_search.new_tags == ["+V", "+AI", "PV/ki+", "+Ind", "+3Pl"]

    lemma1 = Wordform.objects.get(text="pimitâcimow", is_lemma=True)

    search_run.add_result(
        Result(wordform=lemma1, target_language_keyword_match=["crawls"])
    )

    eip_search.inflect_search_results()

    # kî-pimitâcimowak = “they crawled”
    assert list(search_run.unsorted_results())[0].wordform.text == "kî-pimitâcimowak"
