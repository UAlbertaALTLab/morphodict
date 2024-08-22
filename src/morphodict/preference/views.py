from http import HTTPStatus

from django.http import HttpResponse, HttpRequest, Http404
from django.views.decorators.http import require_POST

from morphodict.preference import registry


@require_POST
def change_preference(request: HttpRequest, name: str):
    """
    A view that sets the cookie for the preference named in the URL path.

    NOTE: the path is expected to be the Preference.name, while the parameter is
    expected to be the Preference.cookie_name. These may differ!

        > POST /preference/change/display_mode HTTP/1.1
        > Referer: /search?q=miciw
        > Cookie: mode=old-value
        >
        > mode=new-value

        < HTTP/1.1 302 See Other
        < Set-Cookie: mode=new-value
        < Location: /search?q=miciw
    """
    try:
        preference = registry()[name]
    except KeyError:
        raise Http404(f"Preference does not exist: {name}")

    value = request.POST.get(preference.cookie_name)

    # Tried to set to an unknown choice
    if value not in preference.choices:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    # Make the typechecker see that value is not None after the previous check:
    if value is None:
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    if who_asked_us := request.headers.get("Referer"):
        # Force the browser to refresh the page that issued this request.
        response = HttpResponse(status=HTTPStatus.SEE_OTHER)
        response.headers["Location"] = who_asked_us
    else:
        # We don't know where to redirect, so send no content.
        response = HttpResponse(status=HTTPStatus.NO_CONTENT)

    # NOTE: we're using the Django defaults for the cookie.
    # When left to default, the cookie should last "only as long as the client’s
    # browser session", though... I'm not sure how long that generally is :/
    # See: https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpResponse.set_cookie

    response.set_cookie(preference.cookie_name, value)

    return response
