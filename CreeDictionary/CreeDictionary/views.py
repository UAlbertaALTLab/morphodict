from django.http import HttpResponse
from django.shortcuts import render

from API.models import Inflection
from CreeDictionary.forms import WordSearchForm
from constants import LC, ParadigmSize
from utils import paradigm_filler


def index(request, query_string=None):
    """
    homepage with optional initial query

    :param request:
    :param query_string: initial word and search results to display
    :return:
    """
    context = {"word_search_form": WordSearchForm()}
    if query_string is not None:
        context.update({"query_string": query_string})
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


def search_results(request, query_string: str):
    """
    returns rendered boxes of search results according to user query
    """
    lemmas = Inflection.fetch_lemmas_by_user_query(query_string)
    return render(request, "CreeDictionary/word-entries.html", {"words": lemmas})


def lemma_details(request, lemma_id: int):
    """
    render paradigm table and detailed info of a lemma
    """
    lemma = Inflection.objects.get(id=lemma_id)

    if lemma.lc != "":
        table = paradigm_filler.fill_paradigm(
            lemma.text, LC(lemma.lc), ParadigmSize.BASIC
        )

    else:
        table = []

    return render(
        request, "CreeDictionary/paradigm.html", {"lemma": lemma, "table": table}
    )
