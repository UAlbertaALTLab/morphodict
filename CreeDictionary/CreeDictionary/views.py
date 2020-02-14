from django.http import HttpResponse
from django.shortcuts import render

from API.models import Wordform
from CreeDictionary.forms import WordSearchForm
from constants import SimpleLC, ParadigmSize
from utils import fst_analysis_parser, get_modified_distance


def index(request, query_string=None, lemma_id=None):
    """
    homepage with optional initial query or initial lemma. query_string and lemma_id can not both be given

    :param request:
    :param query_string: optional initial search results to display
    :param lemma_id: optional initial paradigm page to display
    :return:
    """
    lemma = Wordform.objects.get(id=lemma_id) if lemma_id else None
    context = {
        "word_search_form": WordSearchForm(),
        "query_string": query_string,
        "search_results": Wordform.search(query_string) if query_string else set(),
        "lemma_id": lemma_id,
        "lemma": lemma,
        "paradigm_size": ParadigmSize.BASIC.display_form,
        "paradigm_tables": lemma.paradigm if lemma else None,
    }
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


def search_results(request, query_string: str):
    """
    returns rendered boxes of search results according to user query
    """
    results = Wordform.search(query_string)
    return render(
        request, "CreeDictionary/word-entries.html", {"search_results": results}
    )


def lemma_details(request, lemma_id: int):
    """
    render paradigm table for a lemma
    """
    lemma = Wordform.objects.get(id=lemma_id)
    return render(
        request,
        "CreeDictionary/paradigm.html",
        {
            "lemma": lemma,
            "paradigm_size": ParadigmSize.BASIC.display_form,
            "paradigm_tables": lemma.paradigm,
        },
    )


def about(request):
    """
    About page.
    """
    return render(request, "CreeDictionary/about.html")
