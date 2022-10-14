from __future__ import annotations

import json

from http import HTTPStatus
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.http.response import JsonResponse, HttpResponse
from rest_framework.decorators import api_view

from CreeDictionary.API.search import presentation, search_with_affixes
from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.CreeDictionary.paradigm.manager import ParadigmDoesNotExistError
from crkeng.app.preferences import DisplayMode, AnimateEmoji
from morphodict.lexicon.models import Wordform

from .utils import *


@api_view(['GET',])
def word_details_api(request, slug: str):
    """
    Head word detail page. Will render a paradigm, if applicable. Fallback to search
    page if no slug is not found.

    :param slug: the stable unique ID of the lemma
    :return:

    :raise 300 Multiple Choices: the frontend should redirect to /search/?q=<slug>
    :raise 404 Not Found: when the lemma-id or paradigm size isn't found in the database
    """
    lemma = Wordform.objects.filter(slug=slug,is_lemma=True)

    if lemma.count() == 0:
        return HttpResponseNotFound("lemma not found")
    elif lemma.count() > 1:
        # This should only ever come up when the user inputs the url directly. If it does, the frontend should redirect to the search page.
        return HttpResponse(status=HTTPStatus.MULTIPLE_CHOICES)
        
    lemma = lemma.get()

    paradigm_size = ""
    paradigm_sizes = []
    paradigm = lemma.paradigm

    wordform = presentation.serialize_wordform(
        lemma,
        animate_emoji=AnimateEmoji.current_value_from_request(request),
        dict_source=get_dict_source(request)
    )
    wordform = wordform_orth(wordform)

    if paradigm is not None:
        paradigm_manager = default_paradigm_manager()
        try:
            paradigm_sizes = list(paradigm_manager.sizes_of(paradigm))
        except ParadigmDoesNotExistError:
            return HttpResponseNotFound("bad paradigm size")

        if "basic" in paradigm_sizes:
            default_size = "basic"
        else:
            default_size = paradigm_sizes[0]

        if len(paradigm_sizes) <= 1:
            paradigm_size = default_size
        else:
            paradigm_size = request.GET.get("paradigm-size")
            if paradigm_size:
                paradigm_size = paradigm_size.lower()
            if paradigm_size not in paradigm_sizes:
                paradigm_size = default_size

        paradigm = paradigm_for(lemma, paradigm_size)
        paradigm = get_recordings_from_paradigm(paradigm, request)
        paradigm = paradigm_orth(paradigm)

    content = {
        "nipaw_wordform": {
            "lemma_id": lemma.id,
            "wordform": wordform,
            "paradigm": paradigm,
            "paradigm_size": paradigm_size,
            "paradigm_sizes": paradigm_sizes,
        }
    }

    return JsonResponse(content)


@api_view(['POST',])
def search_api(request):
    """
    homepage with optional initial search results to display

    :param request:
    :return:
    """
    query_string = request.data.get("name")
    dict_source = get_dict_source(request)
    search_run = None
    include_auto_definitions = request.user.is_authenticated
    context = dict()

    if query_string:
        search_run = search_with_affixes(
            query_string,
            include_auto_definitions=include_auto_definitions,
        )
        search_results = search_run.serialized_presentation_results(
            display_mode=DisplayMode.current_value_from_request(request),
            dict_source=dict_source,
        )
        did_search = True

    else:
        query_string = ""
        search_results = []
        did_search = False

    context.update(
        word_search_form=request.data.get("name"),
        query_string=query_string,
        search_results=search_results,
        did_search=did_search
    )

    context["show_dict_source_setting"] = settings.SHOW_DICT_SOURCE_SETTING
    if search_run and search_run.verbose_messages and search_run.query.verbose:
        context["verbose_messages"] = json.dumps(
            search_run.verbose_messages, indent=2, ensure_ascii=False
        )

    for result in context["search_results"]:
        result["lemma_wordform"] = wordform_orth(result["lemma_wordform"])
     
    return JsonResponse(context)