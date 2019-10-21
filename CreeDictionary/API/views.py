import time
from typing import Dict, List

from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import render

from API.models import Inflection
from constants import LC
from utils import paradigm_filler, ParadigmSize


# todo: update api documentation


def translate_cree(request, query_string: str) -> JsonResponse:
    """
    click-in-text api

    note: returned definition is for lemma, not the queried inflected form.
    see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/wiki/Web-API for API specifications
    """
    # todo (for matt): rewrite this
    pass
