import time
from typing import Dict

from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render
from hfstol import HFSTOL

from API.models import Inflection
from constants import LC
from utils import paradigm_filler, ParadigmSize
from utils.shared_res_dir import shared_res_dir

descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)


def search(request, query_string):
    """
    api and for internal use when render-html=true is specified
    """
    # todo: change api documentation (originally a git wiki page)
    lemmas: QuerySet = Inflection.fetch_lemmas_by_user_query(query_string)
    response: Dict[str, list] = {}
    if request.GET.get("render-html", False) == "true":
        return render(request, "API/word-entries.html", {"words": lemmas})
    else:
        response["words"] = [lemma.serialize() for lemma in lemmas]
        return JsonResponse(response)


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
