from __future__ import annotations

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from typing import Optional, Any
import logging

from morphodict.frontend.templatetags.morphodict_extras import observed_or_unobserved
from morphodict.orthography.templatetags.morphodict_orth import orth, orth_tag
from morphodict.paradigm.panes import Paradigm
from morphodict.lexicon.models import Wordform

from morphodict.paradigm.manager import ParadigmDoesNotExistError
from morphodict.paradigm.generation import default_paradigm_manager
from morphodict.paradigm.recordings import get_recordings_from_paradigm
from morphodict.relabelling.templatetags.relabelling import relabel


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
        paradigm = get_recordings_from_paradigm(paradigm, **recordings_info(request))
    except ParadigmDoesNotExistError:
        return HttpResponseBadRequest("paradigm does not exist")
    return render(
        request,
        "morphodict/components/paradigm.html",
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size,
            "paradigm": paradigm,
            "show_morphemes": request.COOKIES.get("show_morphemes"),
        },
    )


@require_GET
def paradigm_for_lemma(request):
    """
    Render word-detail.html for a lemma. `index` view function renders a whole page that contains word-detail.html too.
    This function, however, is used by javascript to dynamically replace the paradigm with the ones of different sizes.
    Unlike `paradigm_internal`, we take a lemma and a paradigm layout to produce the paradigm.

    `lemma`, `layout`, and `paradigm-size` are the expected query params in the request

    4xx errors will have a single string as error message

    :raise 400 Bad Request: when the query params are not as expected or inappropriate
    :raise 404 Not Found: when the lemma-id isn't found in the database
    :raise 405 Method Not Allowed: when method other than GET is used
    """
    lemma = request.GET.get("lemma")
    layout = request.GET.get("layout")
    paradigm_size = request.GET.get("paradigm-size")
    show_morphemes = request.GET.get("show_morphemes")
    if not show_morphemes:
        show_morphemes = request.COOKIES.get("show_morphemes")

    manager = default_paradigm_manager()

    try:
        if not (paradigm := manager.paradigm_for(layout, lemma, paradigm_size)):
            return HttpResponseBadRequest("paradigm does not exist")
    except ParadigmDoesNotExistError:
        return HttpResponseBadRequest("paradigm does not exist")

    return render(
        request,
        "morphodict/components/paradigm-api.html",
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size,
            "paradigm": paradigm,
            "show_morphemes": show_morphemes,
        },
    )


@require_GET
def json_paradigm_for_lemma(request):
    """
    Render word-detail.html for a lemma. `index` view function renders a whole page that contains word-detail.html too.
    This function, however, is used by javascript to dynamically replace the paradigm with the ones of different sizes.
    Unlike `paradigm_internal`, we take a lemma and a paradigm layout to produce the paradigm.

    `lemma`, `layout`, and `paradigm-size` are the expected query params in the request

    4xx errors will have a single string as error message

    :raise 400 Bad Request: when the query params are not as expected or inappropriate
    :raise 404 Not Found: when the lemma-id isn't found in the database
    :raise 405 Method Not Allowed: when method other than GET is used
    """
    lemma = request.GET.get("lemma")
    layout = request.GET.get("layout")
    paradigm_size = request.GET.get("paradigm-size")
    show_morphemes = request.GET.get("show_morphemes")
    if not show_morphemes:
        show_morphemes = request.COOKIES.get("show_morphemes")

    manager = default_paradigm_manager()

    try:
        if not (paradigm := manager.paradigm_for(layout, lemma, paradigm_size)):
            return HttpResponseBadRequest("paradigm does not exist")
    except ParadigmDoesNotExistError:
        return HttpResponseBadRequest("paradigm does not exist")

    def serialize(paradigm):
        panes = []
        for pane in paradigm.panes:
            rows = []
            for p_row in pane.tr_rows:
                if p_row.is_header:
                    rows.append({"header": relabel(request, p_row.fst_tags)})
                else:
                    row = []
                    for cell in p_row.cells:
                        if (
                            "should_supress_output" in dir(cell)
                            and cell.should_suppress_output
                        ):
                            row.append({})
                        elif cell.is_label:
                            row.append(
                                {
                                    "scope": cell.label_for,
                                    "row_span": (
                                        cell.row_span if "row_span" in dir(cell) else 1
                                    ),
                                    "label": relabel(request, cell.fst_tags),
                                }
                            )
                        elif cell.is_missing:
                            row.append({"missing": True})
                        elif cell.is_empty:
                            row.append({"empty": True})
                        else:
                            row.append(
                                {
                                    "in_corpus": observed_or_unobserved(
                                        cell.inflection
                                    ),
                                    "inflection": (
                                        orth_tag(request, "·".join(cell.morphemes))
                                        if cell.morphemes
                                        and (
                                            show_morphemes == "everywhere"
                                            or show_morphemes == "paradigm"
                                        )
                                        else cell.inflection
                                    ),
                                }
                            )
                    rows.append(row)
            panes.append({"pane": rows})
        return panes

    json_response = JsonResponse(
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size,
            "paradigm": serialize(paradigm),
            "show_morphemes": show_morphemes,
        }
    )
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


def paradigm_for(wordform: Wordform, paradigm_size: str) -> Optional[Paradigm]:
    """
    Returns a paradigm for the given wordform at the desired size.

    If a paradigm cannot be found, None is returned
    """
    logger = logging.getLogger(__name__)

    manager = default_paradigm_manager()

    if name := wordform.paradigm:
        fst_lemma = wordform.lemma.text if wordform.lemma else None

        if settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT:
            fst_lemma = wordform.lemma.fst_lemma if wordform.lemma else None

        if paradigm := manager.paradigm_for(name, fst_lemma, paradigm_size):
            return paradigm
        logger.warning(
            "Could not retrieve static paradigm %r " "associated with wordform %r",
            name,
            wordform,
        )

    return None


def paradigm_context_for_lemma(lemma: Wordform, request) -> dict[str, Any]:
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

        paradigm = get_recordings_from_paradigm(
            paradigm_for(lemma, size), **recordings_info(request)
        )

        return {"paradigm": paradigm, "paradigm_size": size, "paradigm_sizes": sizes}

    return {}


def recordings_info(request) -> dict:
    if source := request.COOKIES.get("audio_source"):
        if source != "both":
            speech_db_eq = [remove_diacritics(source)]
        else:
            speech_db_eq = settings.SPEECH_DB_EQ
    else:
        speech_db_eq = settings.SPEECH_DB_EQ

    if request.COOKIES.get("synthesized_audio_in_paradigm") == "yes":
        speech_db_eq.insert(0, "synth")

    return {
        "paradigm_audio": not request.COOKIES.get("paradigm_audio") in ["no", None],
        "speech_db_eq": speech_db_eq,
    }


def remove_diacritics(item):
    """
    >>> remove_diacritics("mōswacīhk")
    'moswacihk'
    >>> remove_diacritics("maskwacîs")
    'maskwacis'
    """
    item = item.translate(str.maketrans("ēīōāêîôâ", "eioaeioa"))
    return item
