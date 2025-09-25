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

from nltk.corpus import wordnet as wn

from morphodict.frontend.views import (
    should_include_auto_definitions,
    should_inflect_phrases,
)
from morphodict.lexicon.models import WordNetSynset
from django.db.models import Count

from morphodict.search import (
    api_search,
    rapidwords_index_search,
    wordnet_index_search as wordnet_index_search_internal,
    search_with_affixes,
)
from morphodict.search.presentation import SerializedPresentationResult
from morphodict.search.types import (
    WordnetEntry,
    normalize_wordnet_keyword,
)


class SearchApiDict(TypedDict):
    query_string: str
    search_results: list[SerializedPresentationResult]
    did_search: bool


@require_GET
def click_in_text(request: HttpRequest) -> HttpResponse:
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
def click_in_text_embedded_test(request: HttpRequest):
    if not settings.DEBUG:
        raise Http404()
    return render(request, "API/click-in-text-embedded-test.html")


@require_GET
def rapidwords_index(request: HttpRequest) -> HttpResponse:
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
def wordnet_index(request: HttpRequest) -> HttpResponse:
    """
    rapidwords by index
    see SerializedSearchResult in schema.py for API specifications
    """

    wn = request.GET.get("wn")
    if not wn:
        return HttpResponseBadRequest("index param wn is missing")

    results = wordnet_index_search_internal(index=wn)
    if results:
        response = {"results": results.serialized_presentation_results()}
    else:
        response = {"results": []}

    json_response = JsonResponse(response)
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


@require_GET
def wordnet_synset(request: HttpRequest) -> HttpResponse:
    wn = request.GET.get("wn")
    filter_in_dictionary = request.GET.get("in_dictionary", False)

    if not wn:
        return HttpResponseBadRequest("index param wn is missing")
    try:
        entry = WordnetEntry(wn)
        siblings = [h for hyper in entry.hypernyms() for h in hyper.hyponyms()]
        if not siblings:
            siblings.append(entry)

        hypernyms = [
            {"synset": str(h), "definition": h.definition()} for h in entry.hypernyms()
        ]
        hyponyms = [
            {"synset": str(h), "definition": h.definition()} for h in entry.hyponyms()
        ]
        hyponyms_of_hypernyms = [
            {"synset": str(h), "definition": h.definition()} for h in siblings
        ]

        hyponyms_of_hypernyms_of_hypernyms = [
            {"synset": str(a), "definition": a.definition()}
            for h in entry.hypernyms()
            for hh in h.hypernyms()
            for a in hh.hyponyms()
        ]

        if filter_in_dictionary:
            synsets = (
                {s["synset"] for s in hypernyms}
                | {s["synset"] for s in hyponyms}
                | {s["synset"] for s in hyponyms_of_hypernyms}
                | {s["synset"] for s in hyponyms_of_hypernyms_of_hypernyms}
            )
            check = (
                WordNetSynset.objects.filter(name__in=synsets)
                .annotate(wordforms_count=Count("wordforms"))
                .values("name", "wordforms_count")
            )

            def filter_only_with_wordforms(input):
                def has_wordforms(h):
                    if h["synset"] == wn:
                        # Keep the entry searched as sibling!
                        return True
                    candidate = check.filter(name=h["synset"]).first()
                    return candidate and candidate["wordforms_count"] > 0

                return [h for h in input if has_wordforms(h)]

            hyponyms_of_hypernyms = filter_only_with_wordforms(hyponyms_of_hypernyms)

        json_response = JsonResponse(
            {
                "synset": str(entry),
                "hypernyms": hypernyms,
                "hyponyms": hyponyms,
                "hyponyms_of_hypernyms": hyponyms_of_hypernyms,
                "hyponyms_of_hypernyms_of_hypernyms": hyponyms_of_hypernyms_of_hypernyms,
                "definition": entry.definition(),
            }
        )
        json_response["Access-Control-Allow-Origin"] = "*"
        return json_response
    except:
        return HttpResponseBadRequest("problem with request")


@require_GET
def wordnet_index_search(request: HttpRequest) -> HttpResponse:
    wn_search = request.GET.get("wn")
    if not wn_search:
        return HttpResponseBadRequest("index param wn is missing")
    try:
        entries = [
            WordnetEntry(set)
            for set in wn.synsets(normalize_wordnet_keyword(wn_search))
            if set
        ]
        if not entries:
            try:
                entries.append(WordnetEntry(wn_search))
            except:
                pass
        json_response = JsonResponse(
            {
                "results": [
                    {"synset": str(entry), "definition": entry.definition()}
                    for entry in entries
                ]
            }
        )
        json_response["Access-Control-Allow-Origin"] = "*"
        return json_response
    except:
        return HttpResponseBadRequest("problem with request")


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
