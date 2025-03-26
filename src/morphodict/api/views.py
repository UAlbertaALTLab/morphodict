from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
    Http404,
    HttpRequest,
)
from django.shortcuts import render
from django.views.decorators.http import require_GET
from typing import TypedDict

from crkeng.app.preferences import DictionarySource
from morphodict.frontend.views import (
    should_include_auto_definitions,
    should_inflect_phrases,
)
from morphodict.paradigm.preferences import DisplayMode
from morphodict.search import api_search, rapidwords_index_search, search_with_affixes
from morphodict.search.presentation import SerializedPresentationResult


class SearchApiDict(TypedDict):
    query_string: str
    search_results: list[SerializedPresentationResult]
    did_search: bool


@require_GET
def click_in_text(request) -> HttpResponse:
    """
    click-in-text api
    see SerializedSearchResult in schema.py for API specifications
    """

    q = request.GET.get("q")
    if q is None:
        return HttpResponseBadRequest("query param q missing")
    elif q == "":
        return HttpResponseBadRequest("query param q is an empty string")

    results = api_search(q, include_auto_definitions=False)

    response = {"results": results}

    json_response = JsonResponse(response)
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


@require_GET
def click_in_text_embedded_test(request):
    if not settings.DEBUG:
        raise Http404()
    return render(request, "API/click-in-text-embedded-test.html")


@require_GET
def rapidwords_index(request) -> HttpResponse:
    """
    rapidwords by index
    see SerializedSearchResult in schema.py for API specifications
    """

    rw_index = request.GET.get("rw_index")
    if rw_index is None:
        return HttpResponseBadRequest("index param rw_index is missing")
    elif rw_index == "":
        return HttpResponseBadRequest("index param rw_index is an empty string")

    results = rapidwords_index_search(index=rw_index)
    if results:
        response = {"results": results.serialized_presentation_results()}
    else:
        response = {"results": []}

    json_response = JsonResponse(response)
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


@require_GET
def search_api(request: HttpRequest) -> JsonResponse:
    """
    homepage with optional initial search results to display

    :param request:
    :return:
    """

    query_string = request.GET.get("query")

    json_response = JsonResponse(
        {"query_string": "", "search_results": [], "did_search": False}
    )

    if query_string:
        search_run = search_with_affixes(
            query_string,
            include_auto_definitions=should_include_auto_definitions(request),
            inflect_english_phrases=should_inflect_phrases(request),
        )
        search_results = search_run.serialized_presentation_results()

        json_response = JsonResponse(
            {
                "query_string": query_string,
                "search_results": search_results,
                "did_search": True,
            }
        )

    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response
