from django.http import HttpResponse
from django.shortcuts import render

from API.models import Inflection
from CreeDictionary.forms import WordSearchForm
from constants import LC, ParadigmSize
from utils import paradigm_filler


def index(request, query_string=None, lemma_id=None):
    """
    homepage with optional initial query or initial lemma. query_string and lemma_id can not both be given

    :param request:
    :param query_string: initial search results to display
    :param lemma_id: initial paradigm page to display
    :return:
    """
    context = {"word_search_form": WordSearchForm()}
    if query_string is not None:
        context.update({"query_string": query_string})
    elif lemma_id is not None:
        context.update({"lemma_id": lemma_id})
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


import pysnooper


def search_results(request, query_string: str):
    """
    returns rendered boxes of search results according to user query
    """
    # todo: use the keys of analysis_to_lemmas to show user input analysis (Preverb, reduplication, IC ...)

    analysis_to_lemmas, lemmas_by_english = Inflection.fetch_lemma_by_user_query(
        query_string
    )
    words = [b for a in analysis_to_lemmas.values() for b in a] + lemmas_by_english
    return render(request, "CreeDictionary/word-entries.html", {"words": words})


def lemma_details(request, lemma_id: int):
    """
    render paradigm table for a lemma
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
