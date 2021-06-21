import logging
from typing import Any, Dict, Literal, Union

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

import morphodict.analysis
from morphodict.lexicon.models import Wordform
from CreeDictionary.API.search import presentation, search_with_affixes
from CreeDictionary.CreeDictionary.forms import WordSearchForm
from CreeDictionary.CreeDictionary.paradigm.filler import Row
from CreeDictionary.CreeDictionary.paradigm.generation import (
    default_paradigm_manager,
    generate_paradigm,
)
from CreeDictionary.CreeDictionary.paradigm.panes import Paradigm
from CreeDictionary.phrase_translate.translate import (
    eng_noun_entry_to_inflected_phrase_fst,
    eng_phrase_to_crk_features_fst,
    eng_verb_entry_to_inflected_phrase_fst,
)
from CreeDictionary.utils import ParadigmSize, WordClass
from crkeng.app.preferences import DisplayMode, ParadigmLabel
from morphodict.preference.views import ChangePreferenceView

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
    page if no head is found or multiple heads are found.

    Possible query params:

      To disambiguate the head word (see: Wordform.homograph_disambiguator):
        - pos
        - inflectional_category
        - analysis
        - id

      To affect the paradigm size:

        - paradigm-size (default is BASIC) to specify the size of the paradigm

    :param request: accepts query params `pos` `inflectional_category` `analysis` `id` to further specify query_string
    :param slug: the stable unique ID of the lemma
    """

    lemma = Wordform.objects.filter(slug=slug, is_lemma=True)

    if lemma.count() != 1:
        # The result is either empty or ambiguous; either way, do a search!
        return redirect(url_for_query(slug or ""))

    lemma = lemma.get()
    paradigm_size = ParadigmSize.from_string(request.GET.get("paradigm-size"))
    paradigm = paradigm_for(lemma, paradigm_size)

    context = create_context_for_index_template(
        "word-detail",
        # TODO: rename this to wordform ID
        lemma_id=lemma.id,
        # TODO: remove this parameter in favour of...
        lemma=lemma,
        # ...this parameter
        wordform=presentation.serialize_wordform(lemma),
        paradigm_size=paradigm_size,
        paradigm=paradigm,
    )
    return render(request, "CreeDictionary/index.html", context)


def index(request):  # pragma: no cover
    """
    homepage with optional initial search results to display

    :param request:
    :param query_string: optional initial search results to display
    :return:
    """

    user_query = request.GET.get("q", None)

    if user_query:
        search_results = search_with_affixes(
            user_query,
            include_auto_definitions=should_include_auto_definitions(request),
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
    return render(request, "CreeDictionary/index.html", context)


def search_results(request, query_string: str):  # pragma: no cover
    """
    returns rendered boxes of search results according to user query
    """
    results = search_with_affixes(
        query_string, include_auto_definitions=should_include_auto_definitions(request)
    )
    return render(
        request,
        "CreeDictionary/search-results.html",
        {"query_string": query_string, "search_results": results},
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
        paradigm_size = ParadigmSize(paradigm_size.upper())
    except ValueError:
        return HttpResponseBadRequest(
            f"paradigm-size is not one {[x.value for x in ParadigmSize]}"
        )

    try:
        lemma = Wordform.objects.get(id=lemma_id)
    except Wordform.DoesNotExist:
        return HttpResponseNotFound("specified lemma-id is not found in the database")
    # end guards

    paradigm = paradigm_for(lemma, paradigm_size)
    if isinstance(paradigm, Paradigm):
        template_name = "CreeDictionary/components/paradigm-with-panes.html"
    else:
        template_name = "CreeDictionary/components/paradigm.html"

    return render(
        request,
        template_name,
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size.value,
            "paradigm": paradigm,
        },
    )


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
        assert "paradigm_size" in kwargs, "word detail page requires paradigm_size"
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


class ChangeDisplayMode(ChangePreferenceView):
    """
    Sets the mode= cookie, which affects how search results are rendered.
    """

    preference = DisplayMode  # type: ignore  # mypy can't deal with the decorator :/


class ChangeParadigmLabelPreference(ChangePreferenceView):
    """
    Sets the paradigmlabel= cookie, which affects the type of labels ONLY IN THE
    PARADIGMS!
    """

    preference = ParadigmLabel  # type: ignore  # mypy can't deal with the decorator :/


## Helper functions


def should_include_auto_definitions(request):
    # For now, show auto-translations if and only if the user is logged in
    return request.user.is_authenticated


def disambiguating_filter_from_query_params(query_params: dict[str, str]):
    """
    Sometimes wordforms may have the same text (a.k.a., be homographs/homophones),
    thus need to be disambiguate further before displaying a paradigm.

    This computes the intersection between the provided query parameters and the valid
    disambiguating filters used for homograph disambiguation.
    """
    keys_present = query_params.keys() & {
        # e.g., VTA-1, VTI-3
        # Since inflectional category, by definition, indicates the paradigm of the
        # associated head word, this is the preferred disambiguator. It **should** work
        # most of the time.
        "inflectional_category",
        # e.g., N or V.
        # This is the "general word class"  a.k.a., not enough information to know
        # what paradigm to use. This disambiguator is discouraged.
        "pos",
        # e.g., câhkinêw+V+TA+Ind+5Sg/Pl+4Sg/PlO
        # I'm honestly not sure why this was chosen as a disambiguator ¯\_(ツ)_/¯
        "analysis",
        # Last resort: ephemeral database ID. This is NOT STABLE across database imports!
        "id",
    }
    return {key: query_params[key] for key in keys_present}


def paradigm_for(
    wordform: Wordform, paradigm_size: ParadigmSize
) -> Union[Paradigm, list[list[Row]]]:
    """
    Returns a paradigm for the given wordform at the desired size.

    If a paradigm cannot be found, an empty list is returned
    """
    # TODO: make this use the new-style ParadigmManager exclusively

    manager = default_paradigm_manager()

    if name := wordform.paradigm:
        size = convert_crkeng_paradigm_size_to_size(paradigm_size)

        return manager.paradigm_for(name, lemma=wordform.analysis.lemma, size=size)

    # try returning an old-style paradigm: may return []
    return generate_paradigm(wordform, paradigm_size)


def convert_crkeng_paradigm_size_to_size(paradigm_size: ParadigmSize):
    """
    Returns the crkeng layout size, which is currently:
     - basic
     - full
    """
    return {
        ParadigmSize.FULL: "full",
        ParadigmSize.BASIC: "basic",
        # The linguistic "size" does not, as of yet exist, however its content is
        # exactly the same as the full layout.
        ParadigmSize.LINGUISTIC: "full",
    }[paradigm_size]


def convert_crkeng_word_class_to_paradigm_name(word_class: WordClass):
    """
    Returns the paradigm name in crkeng's layouts directory, or None if a paradigm
    name cannot be determined from the legacy WordClass alone.
    """
    return {
        WordClass.VII: "VII",
        WordClass.VTI: "VTI",
        WordClass.VAI: "VAI",
        WordClass.VTA: "VTA",
        WordClass.NA: "NA",
        WordClass.NI: "NI",
        # uses Arok's scheme: Noun Dependent {Animate/Inanimate}
        WordClass.NAD: "NDA",
        WordClass.NID: "NDI",
    }.get(word_class)
