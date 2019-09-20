import time
from typing import Dict, List

from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render

from API.models import Inflection
from constants import LC
from utils import paradigm_filler, ParadigmSize


def search(request, query_string):
    """
    api and for internal use when render-html=true is specified
    """
    # todo: change api documentation (originally a git wiki page)
    # fixme or not: performance issue
    #   2019/09/18 Matt Yan: for query_string "miteh", fetch_lemmas_by_user_query takes 0.1 seconds on my laptop
    #   render(request, "API/word-entries.html", {"words": lemmas}) takes a whopping 1 full second
    #   side note: somehow I had a hard time finding render() in the report of `pipenv run profile client_query`
    #   I used time.time() in this function instead.

    #   This StackOverflow post talks about how to optimize render()
    #   https://stackoverflow.com/questions/8569387/django-guidelines-for-speeding-up-template-rendering-performance
    #
    #   It was substantially faster previously when the variables passed in were

    # optimization: django template

    # Templating
    response: Dict[str, list] = {}
    # todo: remove render html
    if request.GET.get("render-html", False) == "true":
        a = time.time()
        r = Inflection.fetch_lemmas_by_user_query(query_string)
        print(time.time() - a)
        return render(request, "API/word-entries.html", {"words": r})


def translate_cree(request, query_string: str) -> JsonResponse:
    """
    click-in-text api

    note: returned definition is for lemma, not the queried inflected form.
    see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/wiki/Web-API for API specifications
    """
    # todo (for matt): rewrite this
    pass


def lemma_details(request, lemma_id: int):
    """
    for internal use
    render paradigm table
    """
    # todo (for matt): api documentation

    lemma = Inflection.objects.get(id=lemma_id)

    if lemma.lc != "":
        table = paradigm_filler.fill_paradigm(
            lemma.text, LC(lemma.lc), ParadigmSize.FULL
        )

    else:
        table = []

    return render(request, "API/paradigm.html", {"lemma": lemma, "table": table})
