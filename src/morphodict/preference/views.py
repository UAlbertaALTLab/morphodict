from http import HTTPStatus

from django.http import HttpResponse, HttpRequest, Http404
from django.views import View
from django.views.decorators.http import require_POST

from morphodict.preference import Preference, registry


@require_POST
def change_preference(request: HttpRequest, preference_name: str):
    """
    A view that sets the cookie for the preference named in the URL path:

        > POST /change-preference/mode HTTP/1.1
        > Referer: /search?q=miciw
        > Cookie: mode=old-value
        >
        > mode=new-value

        < HTTP/1.1 302 See Other
        < Set-Cookie: mode=new-value
        < Location: /search?q=miciw
    """
    try:
        preference = registry()[preference_name]
    except KeyError:
        raise Http404(f"Preference does not exist: {preference_name}")

    return _change_preference_cookie(request, preference)


class ChangePreferenceView(View):
    """
    A generic view (class-based view) that sets the cookie for a preference.

    Usage:

        # views.py
        class ChangeMyPreference(ChangePreferenceView):
            preference = MyPreferenceSubclass

        # urls.py
        urlpatterns = [
            ...,
            path("change-my-preference, ChangeMyPreference.as_view()),
        ]

    Uses cookie name, and options from the given preference.

        > POST /change-preference HTTP/1.1
        > Referer: /search?q=miciw
        > Cookie: preference=old-value
        >
        > preference=new-value

        < HTTP/1.1 302 See Other
        < Set-Cookie: mode=linguistic
        < Location: /search?q=miciw

    See also: https://docs.djangoproject.com/en/3.2/topics/class-based-views/
    """

    preference: Preference

    def post(self, request) -> HttpResponse:
        preference = self.preference
        return _change_preference_cookie(request, preference)


def _change_preference_cookie(request: HttpRequest, preference: Preference):
    """
    Shared implementation for changing a preference.
    """

    # TODO: let preferences share ONE cookie
    value = request.POST.get(preference.cookie_name)

    # Tried to set to an unknown choice
    if value not in preference.choices:
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
