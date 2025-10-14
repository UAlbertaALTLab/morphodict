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
from typing import Any, TypedDict

from nltk.corpus import wordnet as wn

from morphodict.frontend.views import (
    should_include_auto_definitions,
    should_inflect_phrases,
)
from morphodict.lexicon.models import WordNetSynset, Wordform
from django.db.models import Count, QuerySet, Sum

from morphodict.analysis import rich_analyze_relaxed
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

    try:
        entry = WordnetEntry(wn)
        hyponym_entries = entry.hyponyms()
        generate_api_repr_with_counts = generate_api_counts_with_prefetch(
            WordNetSynset.objects.filter(
                name__in={str(h) for h in hyponym_entries} | {str(entry)}
            )
            .annotate(wordforms_count=Count("wordforms", distinct=True))
            .values("name", "wordforms_count")
        )

        hyponyms = generate_api_repr_with_counts(hyponym_entries, True)
    except:
        hyponyms = []

    response = {
        "results": results.serialized_presentation_results() if results else [],
        "hyponyms": hyponyms,
    }

    json_response = JsonResponse(response)
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


def generate_api_counts_with_prefetch(
    wordforms_in_synsets: QuerySet[WordNetSynset, dict[str, Any]],
):
    def generate_api_repr_with_counts(
        entries: list[WordnetEntry], add_closure_count: bool = False
    ):
        answer = []
        for entry in entries:
            api_repr = entry.api_repr()
            api_repr["wordform_count"] = wordforms_in_synsets.filter(
                name=api_repr["synset"]
            ).aggregate(Sum("wordforms_count", default=0))["wordforms_count__sum"]
            if add_closure_count:
                api_repr["wordform_closure_count"] = wordforms_in_synsets.filter(
                    name__in={str(a) for a in entry.hyponyms_closure()} | {str(entry)}
                ).aggregate(Sum("wordforms_count", default=0))["wordforms_count__sum"]
            answer.append(api_repr)
        return answer

    return generate_api_repr_with_counts


@require_GET
def wordnet_synset(request: HttpRequest) -> HttpResponse:
    """
    GET api takes one parameter, wn.
    wn should be a wordnet synset identifier in the format presented in morphodict.
    """
    wn = request.GET.get("wn")

    if not wn:
        return HttpResponseBadRequest("index param wn is missing")
    try:
        entry = WordnetEntry(wn)
        hypernyms = entry.hypernyms()
        hyponyms = entry.hyponyms()
        hyponyms_of_hypernyms = {
            hypo for hyper in hypernyms for hypo in hyper.hyponyms()
        }
        if not hyponyms_of_hypernyms:
            hyponyms_of_hypernyms.add(entry)
        hyponyms_of_hypernyms_of_hypernyms = {
            hhh for h in hypernyms for hh in h.hypernyms() for hhh in hh.hyponyms()
        }

        synsets = {
            str(we)
            for we in hypernyms
            + hyponyms
            + list(hyponyms_of_hypernyms)
            + list(hyponyms_of_hypernyms_of_hypernyms)
            + [hh for h in hyponyms for hh in h.hyponyms_closure()]
        }

        generate_api_repr_with_counts = generate_api_counts_with_prefetch(
            WordNetSynset.objects.filter(name__in=synsets)
            .annotate(wordforms_count=Count("wordforms", distinct=True))
            .values("name", "wordforms_count")
        )

        json_response = JsonResponse(
            {
                "synset": str(entry),
                "hypernyms": generate_api_repr_with_counts(hypernyms),
                "hyponyms": generate_api_repr_with_counts(hyponyms, True),
                "hyponyms_of_hypernyms": generate_api_repr_with_counts(
                    [h for h in hyponyms_of_hypernyms]
                ),
                "hyponyms_of_hypernyms_of_hypernyms": generate_api_repr_with_counts(
                    [h for h in hyponyms_of_hypernyms_of_hypernyms]
                ),
                "definition": entry.definition(),
            }
        )
        json_response["Access-Control-Allow-Origin"] = "*"
        return json_response
    except Exception as e:
        return HttpResponseBadRequest("problem with request")


@require_GET
def wordnet_index_search(request: HttpRequest) -> HttpResponse:
    wn_search = request.GET.get("wn")
    if not wn_search:
        return HttpResponseBadRequest("index param wn is missing")
    try:
        entries = {
            WordnetEntry(set)
            for set in wn.synsets(normalize_wordnet_keyword(wn_search))
            if set
        }
        if not entries:
            try:
                entries.add(WordnetEntry(wn_search))
            except:
                # There's no wordnet category, so search for target language words
                pass
            if not entries:
                wordforms = Wordform.objects.filter(
                    raw_analysis__in={a.tuple for a in rich_analyze_relaxed(wn_search)}
                )
                for wordform in wordforms:
                    entries.update(
                        {WordnetEntry(entry.name) for entry in wordform.synsets.all()}
                    )

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
