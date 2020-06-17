from http import HTTPStatus

from django.views.decorators.http import require_GET

from API.models import Wordform
from CreeDictionary.forms import WordSearchForm
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views import View
from utils import ORTHOGRAPHY_NAME, ParadigmSize

from .utils import url_for_query

# "pragma: no cover" works with coverage.
# It excludes the clause or line (could be a function/class/if else block) from coverage
# it should be used on the view functions that are well covered by integration tests


def lemma_details(request, lemma_text: str = None):  # pragma: no cover
    """
    lemma detail page. Fall back to search page if no lemma is found or multiple lemmas are found

    possible query params are "pos"/"inflectional_category"/"analysis"/"id" to further specify the lemma,
    "paradigm-size" (default is BASIC) to specify the size of the paradigm

    :param request: accepts query params `pos` `inflectional_category` `analysis` `id` to further specify query_string
    :param lemma_text: the exact form of the lemma (no spell relaxation)
    """
    extra_constraints = {
        k: v
        for k, v in request.GET.items()
        if k in {"pos", "inflectional_category", "analysis", "id"}
    }

    paradigm_size = request.GET.get("paradigm-size")
    if paradigm_size is None:
        paradigm_size = ParadigmSize.BASIC
    else:
        paradigm_size = ParadigmSize(paradigm_size.upper())

    filter_args = dict(is_lemma=True, **extra_constraints)
    if lemma_text is not None:
        filter_args["text"] = lemma_text

    lemma = Wordform.objects.filter(**filter_args)
    if lemma.count() == 1:
        lemma = lemma.get()
        context = {
            "lemma_id": lemma.id,
            "lemma": lemma,
            "paradigm_size": paradigm_size,
            "paradigm_tables": lemma.get_paradigm_layouts(size=paradigm_size)
            if lemma
            else None,
        }
        return HttpResponse(render(request, "CreeDictionary/index.html", context))
    else:
        return redirect(url_for_query(lemma_text or ""))


def index(request):  # pragma: no cover
    """
    homepage with optional initial search results to display

    :param request:
    :param query_string: optional initial search results to display
    :return:
    """

    user_query = request.GET.get("q", None)

    if user_query:
        search_results = [
            search_result.serialize() for search_result in Wordform.search(user_query)
        ]
        did_search = True
    else:
        search_results = []
        did_search = False

    context = {
        "word_search_form": WordSearchForm(),
        # when we have initial query word to search and display
        "query_string": user_query,
        "search_results": search_results,
        "did_search": did_search,
    }
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


def search_results(request, query_string: str):  # pragma: no cover
    """
    returns rendered boxes of search results according to user query
    """
    results = Wordform.search(query_string)
    return render(
        request,
        "CreeDictionary/word-entries.html",
        {
            "query_string": query_string,
            "search_results": [r.serialize() for r in results],
        },
    )


@require_GET
def lemma_details_internal(request):
    """
    Render paradigm.html for a lemma. `index` view function renders a whole page that contains paradigm.html too.
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
        assert float(lemma_id) == int(lemma_id)
        lemma_id = int(lemma_id)
    except (ValueError, AssertionError):
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

    return render(
        request,
        "CreeDictionary/paradigm.html",
        {
            "lemma": lemma,
            "paradigm_size": paradigm_size.display_form,
            "paradigm_tables": lemma.get_paradigm_layouts(size=paradigm_size),
        },
    )


def about(request):  # pragma: no cover
    """
    About page.
    """
    return render(request, "CreeDictionary/about.html")


def contact_us(request):  # pragma: no cover
    """
    Contact us page.
    """
    return render(request, "CreeDictionary/contact-us.html")


class ChangeOrthography(View):
    """
    Sets the orth= cookie, which affects the default rendered orthography.

        > POST /change-orthography HTTP/1.1
        > Cookie: orth=Latn
        >
        > orth=Cans

        < HTTP/1.1 204 No Content
        < Set-Cookie: orth=Cans

    Supports only POST requests for now.
    """

    AVAILABLE_ORTHOGRAPHIES = tuple(ORTHOGRAPHY_NAME.keys())

    def post(self, request):
        orth = request.POST.get("orth")

        # Tried to set to an unsupported orthography
        if orth not in self.AVAILABLE_ORTHOGRAPHIES:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        response = HttpResponse(status=HTTPStatus.NO_CONTENT)
        response.set_cookie("orth", orth)
        return response


def redirect_search(request, query_string: str):
    """
    Permanently redirect from old search URL to new search URL.

        /search/TERM -> /search?q=TERM

    """
    return redirect(url_for_query(query_string), permanent=True)
