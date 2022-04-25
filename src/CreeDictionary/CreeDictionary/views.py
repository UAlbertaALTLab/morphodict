from __future__ import annotations

import json
import logging
import urllib
import numpy as np
from typing import Any, Dict, Literal, Optional

import json

from http import HTTPStatus
from django.http.response import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import paradigm_panes

from .utils import *

import requests
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

import morphodict.analysis
from CreeDictionary.API.search import presentation, search_with_affixes
from CreeDictionary.CreeDictionary.forms import WordSearchForm
from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.phrase_translate.translate import (
    eng_noun_entry_to_inflected_phrase_fst,
    eng_phrase_to_crk_features_fst,
    eng_verb_entry_to_inflected_phrase_fst,
)
from crkeng.app.preferences import DisplayMode, AnimateEmoji, ShowEmoji
from morphodict.lexicon.models import Wordform

from .paradigm.manager import ParadigmDoesNotExistError
from .paradigm.panes import Paradigm
from .utils import url_for_query

# The index template expects to be rendered in the following "modes";
# The mode dictates which variables MUST be present in the context.
IndexPageMode = Literal["home-page", "search-page", "word-detail", "info-page"]

logger = logging.getLogger(__name__)


# "pragma: no cover" works with coverage.
# It excludes the clause or line (could be a function/class/if else block) from coverage
# it should be used on the view functions that are well covered by integration tests


def entry_details(request, slug: str):
    """
    Head word detail page. Will render a paradigm, if applicable. Fallback to search
    page if no slug is not found.

    :param slug: the stable unique ID of the lemma
    """
    lemma = Wordform.objects.filter(slug=slug, is_lemma=True)

    if lemma.count() != 1:
        # The result is either empty or ambiguous; either way, do a search!
        return redirect(url_for_query(slug.split("@")[0] or ""))

    lemma = lemma.get()

    if rich_analysis := lemma.analysis:
        morphemes = rich_analysis.generate_with_morphemes(lemma.text)
    else:
        morphemes = None

    paradigm_context: dict[str, Any] = {}

    paradigm = lemma.paradigm
    if paradigm is not None:
        paradigm_manager = default_paradigm_manager()
        sizes = list(paradigm_manager.sizes_of(paradigm))
        if "basic" in sizes:
            default_size = "basic"
        else:
            default_size = sizes[0]

        if len(sizes) <= 1:
            size = default_size
        else:
            size = request.GET.get("paradigm-size")
            if size:
                size = size.lower()
            if size not in sizes:
                size = default_size

        paradigm = paradigm_for(lemma, size)
        paradigm = get_recordings_from_paradigm(paradigm, request)

        paradigm_context.update(
            paradigm=paradigm, paradigm_size=size, paradigm_sizes=sizes
        )

    animate_emoji = AnimateEmoji.current_value_from_request(request)  # type: ignore
    dict_source = get_dict_source(request)  # type: ignore
    should_show_emoji = ShowEmoji.current_value_from_request(request)  # type: ignore
    context = create_context_for_index_template(
        "word-detail",
        # TODO: rename this to wordform ID
        lemma_id=lemma.id,
        # TODO: remove this parameter in favour of...
        lemma=lemma,
        # ...this parameter
        wordform=presentation.serialize_wordform(
            lemma,
            animate_emoji=animate_emoji,
            dict_source=dict_source,
            show_emoji=should_show_emoji,
        ),
        **paradigm_context,
    )
    context["show_morphemes"] = request.COOKIES.get("show_morphemes")
    context["morphemes"] = morphemes
    return render(request, "CreeDictionary/index.html", context)


def index(request):  # pragma: no cover
    """
    homepage with optional initial search results to display

    :param request:
    :param query_string: optional initial search results to display
    :return:
    """

    user_query = request.GET.get("q", None)
    dict_source = get_dict_source(request)
    search_run = None

    if user_query:
        include_auto_definitions = should_include_auto_definitions(request)
        search_run = search_with_affixes(
            user_query,
            include_auto_definitions=include_auto_definitions,
        )
        search_results = search_run.serialized_presentation_results(
            display_mode=DisplayMode.current_value_from_request(request),
            animate_emoji=AnimateEmoji.current_value_from_request(request),
            show_emoji=ShowEmoji.current_value_from_request(request),
            dict_source=dict_source,
        )
        did_search = True

    else:
        search_results = []
        did_search = False

    if did_search:
        mode = "search-page"
    else:
        mode = "home-page"

    context = create_context_for_index_template(
        mode,
        word_search_form=WordSearchForm(),
        # when we have initial query word to search and display
        query_string=user_query,
        search_results=search_results,
        did_search=did_search,
    )
    context["show_dict_source_setting"] = settings.SHOW_DICT_SOURCE_SETTING
    context["show_morphemes"] = request.COOKIES.get("show_morphemes")
    if search_run and search_run.verbose_messages and search_run.query.verbose:
        context["verbose_messages"] = json.dumps(
            search_run.verbose_messages, indent=2, ensure_ascii=False
        )
    return render(request, "CreeDictionary/index.html", context)


def search_results(request, query_string: str):  # pragma: no cover
    """
    returns rendered boxes of search results according to user query
    """
    dict_source = get_dict_source(request)  # type: ignore
    include_auto_definitions = should_include_auto_definitions(request)
    results = search_with_affixes(
        query_string, include_auto_definitions=include_auto_definitions
    ).serialized_presentation_results(
        # mypy cannot infer this property, but it exists!
        display_mode=DisplayMode.current_value_from_request(request),  # type: ignore
        animate_emoji=AnimateEmoji.current_value_from_request(request),  # type: ignore
        show_emoji=ShowEmoji.current_value_from_request(request),  # type: ignore
        dict_source=dict_source,
    )

    return render(
        request,
        "CreeDictionary/search-results.html",
        {
            "query_string": query_string,
            "search_results": results,
            "show_morphemes": request.COOKIES.get("show_morphemes"),
        },
    )


@require_GET
def paradigm_internal(request):
    """
    Render word-detail.html for a lemma. `index` view function renders a whole page that contains word-detail.html too.
    This function, however, is used by javascript to dynamically replace the paradigm with the ones of different sizes.

    `lemma-id` and `paradigm-size` are the expected query params in the request

    4xx errors will have a single string as error message

    :raise 400 Bad Request: when the query params are not as expected or inappropriate
    :raise 404 Not Found: when the lemma-id isn't found in the database
    :raise 405 Method Not Allowed: when method other than GET is used
    """
    lemma_id = request.GET.get("lemma-id")
    paradigm_size = request.GET.get("paradigm-size")
    # guards
    if lemma_id is None or paradigm_size is None:
        return HttpResponseBadRequest("query params missing")
    try:
        lemma_id = int(lemma_id)
    except ValueError:
        return HttpResponseBadRequest("lemma-id should be a non-negative integer")
    else:
        if lemma_id < 0:
            return HttpResponseBadRequest(
                "lemma-id is negative and should be non-negative"
            )

    try:
        lemma = Wordform.objects.get(id=lemma_id, is_lemma=True)
    except Wordform.DoesNotExist:
        return HttpResponseNotFound("specified lemma-id is not found in the database")
    # end guards

    try:
        paradigm = paradigm_for(lemma, paradigm_size)
        paradigm = get_recordings_from_paradigm(paradigm, request)
    except ParadigmDoesNotExistError:
        return HttpResponseBadRequest("paradigm does not exist")
    return render(
        request,
        "CreeDictionary/components/paradigm.html",
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size,
            "paradigm": paradigm,
            "show_morphemes": request.COOKIES.get("show_morphemes"),
        },
    )


def settings_page(request):
    # TODO: clean up template so that this weird hack is no longer needed.
    context = create_context_for_index_template("info-page")
    context["show_dict_source_setting"] = settings.SHOW_DICT_SOURCE_SETTING
    return render(request, "CreeDictionary/settings.html", context)


def about(request):  # pragma: no cover
    """
    About page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "CreeDictionary/about.html",
        context,
    )


def contact_us(request):  # pragma: no cover
    """
    Contact us page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "CreeDictionary/contact-us.html",
        context,
    )


def legend(request):  # pragma: no cover
    """
    Legend of abbreviations page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "CreeDictionary/legend.html",
        context,
    )


def query_help(request):  # pragma: no cover
    """
    Query help page. Not yet linked from any public parts of site.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "CreeDictionary/query-help.html",
        context,
    )


@staff_member_required()
def fst_tool(request):
    context = {}

    context["fst_tool_samples"] = settings.FST_TOOL_SAMPLES

    text = request.GET.get("text", None)
    if text is not None:
        context.update({"text": text, "repr_text": repr(text)})

    def decode_foma_results(fst, query):
        return [r.decode("UTF-8") for r in fst[query]]

    if text is not None:
        context["analyses"] = {
            "relaxed_analyzer": morphodict.analysis.relaxed_analyzer().lookup(text),
            "strict_analyzer": morphodict.analysis.strict_analyzer().lookup(text),
            "strict_generator": morphodict.analysis.strict_generator().lookup(text),
            "eng_noun_entry2inflected-phrase": decode_foma_results(
                eng_noun_entry_to_inflected_phrase_fst(), text
            ),
            "eng_verb_entry2inflected-phrase": decode_foma_results(
                eng_verb_entry_to_inflected_phrase_fst(), text
            ),
            "eng_phrase_to_crk_features": decode_foma_results(
                eng_phrase_to_crk_features_fst(), text
            ),
        }

    return render(request, "CreeDictionary/fst-tool.html", context)


def create_context_for_index_template(mode: IndexPageMode, **kwargs) -> Dict[str, Any]:
    """
    Creates the context vars for anything using the CreeDictionary/index.html template.
    """

    context: Dict[str, Any]

    if mode in ("home-page", "info-page"):
        context = {"should_hide_prose": False, "displaying_paradigm": False}
    elif mode == "search-page":
        context = {"should_hide_prose": True, "displaying_paradigm": False}
    elif mode == "word-detail":
        context = {"should_hide_prose": True, "displaying_paradigm": True}
        assert "lemma_id" in kwargs, "word detail page requires lemma_id"
    else:
        raise AssertionError("should never happen")
    # Note: there will NEVER be a case where should_hide_prose=False
    # and displaying_paradigm=True -- that means show an info (like home, about,
    # contact us, etc. AND show a word paradigm at the same time

    context.update(kwargs)

    # Templates require query_string and did_search pair:
    context.setdefault("query_string", "")
    context.setdefault("did_search", False)

    return context


def google_site_verification(request):
    code = settings.GOOGLE_SITE_VERIFICATION
    return HttpResponse(
        f"google-site-verification: google{code}.html",
        content_type="text/html; charset=UTF-8",
    )


## Helper functions


def should_include_auto_definitions(request):
    # For now, show auto-translations if and only if the user is logged in
    return request.user.is_authenticated


def get_dict_source(request):
    if dictionary_source := request.COOKIES.get("dictionary_source"):
        if dictionary_source:
            ret = dictionary_source.split("+")
            ret = [r.upper() for r in ret]
            return ret
    return None


def paradigm_for(wordform: Wordform, paradigm_size: str) -> Optional[Paradigm]:
    """
    Returns a paradigm for the given wordform at the desired size.

    If a paradigm cannot be found, None is returned
    """

    manager = default_paradigm_manager()

    if name := wordform.paradigm:
        fst_lemma = wordform.lemma.text

        if settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT:
            fst_lemma = wordform.lemma.fst_lemma

        if paradigm := manager.paradigm_for(name, fst_lemma, paradigm_size):
            return paradigm
        logger.warning(
            "Could not retrieve static paradigm %r " "associated with wordform %r",
            name,
            wordform,
        )

    return None


def get_recordings_from_paradigm(paradigm, request):
    if request.COOKIES.get("paradigm_audio") in ["no", None]:
        return paradigm

    query_terms = []
    matched_recordings = {}
    speech_db_eq = settings.SPEECH_DB_EQ
    if speech_db_eq == ["_"]:
        return paradigm

    if request.COOKIES.get("synthesized_audio_in_paradigm") == "yes":
        speech_db_eq.append("synth")

    for pane in paradigm.panes:
        for row in pane.tr_rows:
            if not row.is_header:
                for cell in row.cells:
                    if cell.is_inflection:
                        query_terms.append(str(cell))

    for search_terms in divide_chunks(query_terms, 30):
        for source in speech_db_eq:
            url = f"https://speech-db.altlab.app/{source}/api/bulk_search"
            matched_recordings.update(get_recordings_from_url(search_terms, url))

    for pane in paradigm.panes:
        for row in pane.tr_rows:
            if not row.is_header:
                for cell in row.cells:
                    if cell.is_inflection:
                        if str(cell) in matched_recordings:
                            cell.add_recording(matched_recordings[str(cell)])

    return paradigm


def get_recordings_from_url(search_terms, url):
    matched_recordings = {}
    query_params = [("q", term) for term in search_terms]
    response = requests.get(url + "?" + urllib.parse.urlencode(query_params))
    recordings = response.json()

    for recording in recordings["matched_recordings"]:
        matched_recordings[recording["wordform"]] = recording["recording_url"]

    return matched_recordings


# Yield successive n-sized
# chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(terms, size):
    # looping till length l
    for i in range(0, len(terms), size):
        yield terms[i : i + size]


@api_view(['GET', ])
def word_details_api(request, slug: str):
    """
    Head word detail page. Will render a paradigm, if applicable. Fallback to search
    page if no slug is not found.

    :param slug: the stable unique ID of the lemma
    :return:

    :raise 300 Multiple Choices: the frontend should redirect to /search/?q=<slug>
    :raise 404 Not Found: when the lemma-id or paradigm size isn't found in the database
    """
    lemma = Wordform.objects.filter(slug=slug, is_lemma=True)

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
        show_emoji=ShowEmoji.current_value_from_request(request),
        dict_source=get_dict_source(request)
    )
    wordform = wordform_orth(wordform)

    if paradigm is not None:
        FST_DIR = settings.BASE_DIR / "resources" / "fst"
        paradigm_manager = default_paradigm_manager()
        pane_generator = paradigm_panes.PaneGenerator()
        pane_generator.set_layouts_dir(settings.LAYOUTS_DIR)
        pane_generator.set_fst_filepath(FST_DIR / settings.STRICT_GENERATOR_FST_FILENAME)
        try:
            paradigm_sizes = list(paradigm_manager.sizes_of(paradigm))
        except ParadigmDoesNotExistError:
            return HttpResponseNotFound("bad paradigm size")

        if "full" in paradigm_sizes:
            default_size = "full"
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

        paradigm = pane_generator.generate_pane(lemma, paradigm, paradigm_size)
        paradigm = get_recordings_from_paradigm(paradigm, request)
        paradigm = paradigm_orth(paradigm)

    content = {
        "entry": {
            "lemma_id": lemma.id,
            "wordform": wordform,
            "paradigm": paradigm,
            "paradigm_size": paradigm_size,
            "paradigm_sizes": paradigm_sizes,
        }
    }

    return JsonResponse(content)


@api_view(['POST', ])
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
