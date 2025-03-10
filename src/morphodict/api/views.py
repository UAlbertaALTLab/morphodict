from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, Http404
from django.shortcuts import render

from morphodict.search import api_search, rapidwords_index_search


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


def click_in_text_embedded_test(request):
    if not settings.DEBUG:
        raise Http404()
    return render(request, "API/click-in-text-embedded-test.html")


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
