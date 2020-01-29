from django.http import HttpResponse
from django.shortcuts import render

from API.models import Wordform
from CreeDictionary.forms import WordSearchForm
from constants import SimpleLC, ParadigmSize
from shared import paradigm_filler
from utils import fst_analysis_parser, get_modified_distance


def index(request, query_string=None, lemma_id=None):
    """
    homepage with optional initial query or initial lemma. query_string and lemma_id can not both be given

    :param request:
    :param query_string: initial search results o display
    :param lemma_id: initial paradigm page to display
    :return:
    """
    context = {
        "word_search_form": WordSearchForm(),
        "query_string": query_string,
        "lemma_id": lemma_id,
    }
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


def search_results(request, query_string: str):
    """
    returns rendered boxes of search results according to user query
    """
    # todo: show user query analysis (Preverb, reduplication, IC ...)
    results = Wordform.search(query_string)
    return render(request, "CreeDictionary/word-entries.html", {"results": results},)


# todo: allow different paradigm size
def lemma_details(request, lemma_id: int):
    """
    render paradigm table for a lemma
    """
    lemma = Wordform.objects.get(id=lemma_id)
    slc = fst_analysis_parser.extract_simple_lc(lemma.analysis)
    if slc is not None:
        tables = paradigm_filler.fill_paradigm(lemma.text, slc, ParadigmSize.BASIC)
    else:
        tables = []

    return render(
        request,
        "CreeDictionary/paradigm.html",
        {
            "lemma": lemma,
            "paradigm_size": ParadigmSize.BASIC.display_form,
            "tables": tables,
        },
    )


def about(request):
    """
    About page.
    """
    return render(request, "CreeDictionary/about.html")
