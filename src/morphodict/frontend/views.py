from __future__ import annotations

import json
import logging

from typing import Any, Dict, Literal

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

import morphodict.analysis
from morphodict.search import presentation, search_with_affixes
from django.contrib.auth import logout
from morphodict.frontend.forms import WordSearchForm
from morphodict.paradigm.views import paradigm_context_for_lemma
from morphodict.phrase_translate.fst import (
    fst_analyses as phrase_translate_fst_analyses,
)
from crkeng.app.preferences import DisplayMode, AnimateEmoji, ShowEmoji
from morphodict.lexicon.models import Wordform


from morphodict.utils.views import url_for_query

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
    lemmas = Wordform.objects.filter(slug=slug, is_lemma=True)

    if lemmas.count() != 1:
        # The result is either empty or ambiguous; either way, do a search!
        return redirect(url_for_query(slug.split("@")[0] or ""))

    lemma = lemmas.get()

    if rich_analysis := lemma.analysis:
        morphemes = rich_analysis.generate_with_morphemes(lemma.text)
    else:
        morphemes = None

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
        **paradigm_context_for_lemma(lemma, request),
    )
    context["show_morphemes"] = request.COOKIES.get("show_morphemes")
    context["morphemes"] = morphemes
    context["show_ic"] = request.COOKIES.get("show_inflectional_category")
    return render(request, "morphodict/index.html", context)


def index(request):  # pragma: no cover
    """
    homepage with optional initial search results to display

    :param request:
    :param query_string: optional initial search results to display
    :return:
    """

    if settings.MORPHODICT_REQUIRES_LOGIN_IN_GROUP:
        if not request.user.is_authenticated:
            return redirect("/accounts/login/?next=%s" % request.path)
        else:
            groupnames = [x["name"] for x in request.user.groupsvalues("name")]
            if settings.MORPHODICT_REQUIRES_LOGIN_IN_GROUP not in groupnames:
                logout(request)
                return redirect("/accounts/login/?next=%s" % request.path)

    user_query = request.GET.get("q", None)
    dict_source = get_dict_source(request)
    search_run = None

    if user_query:
        include_auto_definitions = should_include_auto_definitions(request)
        inflect_english_phrases = should_inflect_phrases(request)
        search_run = search_with_affixes(
            user_query,
            include_auto_definitions=include_auto_definitions,
            inflect_english_phrases=inflect_english_phrases,
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
    context["show_ic"] = request.COOKIES.get("show_inflectional_category")
    if search_run and search_run.verbose_messages and search_run.query.verbose:
        context["verbose_messages"] = json.dumps(
            search_run.verbose_messages, indent=2, ensure_ascii=False
        )
    return render(request, "morphodict/index.html", context)


def search_results(request, query_string: str):  # pragma: no cover
    """
    returns rendered boxes of search results according to user query
    """
    dict_source = get_dict_source(request)  # type: ignore
    include_auto_definitions = should_include_auto_definitions(request)
    inflect_english_phrases = should_inflect_phrases(request)
    results = search_with_affixes(
        query_string,
        include_auto_definitions=include_auto_definitions,
        inflect_english_phrases=inflect_english_phrases,
    ).serialized_presentation_results(
        # mypy cannot infer this property, but it exists!
        display_mode=DisplayMode.current_value_from_request(request),  # type: ignore
        animate_emoji=AnimateEmoji.current_value_from_request(request),  # type: ignore
        show_emoji=ShowEmoji.current_value_from_request(request),  # type: ignore
        dict_source=dict_source,
    )

    return render(
        request,
        "morphodict/search-results.html",
        {
            "query_string": query_string,
            "search_results": results,
            "show_morphemes": request.COOKIES.get("show_morphemes"),
            "show_ic": request.COOKIES.get("show_inflectional_category"),
        },
    )


def settings_page(request):
    # TODO: clean up template so that this weird hack is no longer needed.
    context = create_context_for_index_template("info-page")
    context["show_dict_source_setting"] = settings.SHOW_DICT_SOURCE_SETTING
    return render(request, "morphodict/settings.html", context)


def about(request):  # pragma: no cover
    """
    About page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "morphodict/about.html",
        context,
    )


def contact_us(request):  # pragma: no cover
    """
    Contact us page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "morphodict/contact-us.html",
        context,
    )


def legend(request):  # pragma: no cover
    """
    Legend of abbreviations page.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "morphodict/legend.html",
        context,
    )


def query_help(request):  # pragma: no cover
    """
    Query help page. Not yet linked from any public parts of site.
    """
    context = create_context_for_index_template("info-page")
    return render(
        request,
        "morphodict/query-help.html",
        context,
    )


@staff_member_required
def fst_tool(request):
    context = {}

    context["fst_tool_samples"] = settings.FST_TOOL_SAMPLES

    text = request.GET.get("text", None)
    if text is not None:
        context.update({"text": text, "repr_text": repr(text)})

    if text is not None:
        context["analyses"] = {
            "relaxed_analyzer": morphodict.analysis.relaxed_analyzer().lookup(text),
            "strict_analyzer": morphodict.analysis.strict_analyzer().lookup(text),
            "strict_generator": morphodict.analysis.strict_generator().lookup(text),
        }
        context["analyses"].update(phrase_translate_fst_analyses(text))

    return render(request, "morphodict/fst-tool.html", context)


def create_context_for_index_template(mode: IndexPageMode, **kwargs) -> Dict[str, Any]:
    """
    Creates the context vars for anything using the morphodict/index.html template.
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
    return False if request.COOKIES.get("auto_translate_defs") == "no" else True


def should_inflect_phrases(request):
    return False if request.COOKIES.get("inflect_english_phrase") == "no" else True


def get_dict_source(request):
    if dictionary_source := request.COOKIES.get("dictionary_source"):
        if dictionary_source:
            ret = dictionary_source.split("+")
            ret = [r.upper() for r in ret]
            return ret
    return None
