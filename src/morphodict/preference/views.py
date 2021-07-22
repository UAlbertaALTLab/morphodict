from http import HTTPStatus

from django.http import HttpResponse
from django.views import View

from morphodict.preference import Preference


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

    @property
    def cookie_name(self):
        return self.preference.cookie_name

    @property
    def choices(self):
        return self.preference.choices

    def post(self, request) -> HttpResponse:
        preference = self.preference

        # TODO: let preferences share ONE cookie
        value = request.POST.get(preference.cookie_name)

        # Tried to set to an unknown display mode
        if value not in preference.choices:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        if who_asked_us := request.headers.get("Referer"):
            # Force the browser to refresh the page that issued this request.
            response = HttpResponse(status=HTTPStatus.SEE_OTHER)
            response.headers["Location"] = who_asked_us
        else:
            # We don't know where to redirect, so send no content.
            # (also, this probably should never happen?)
            response = HttpResponse(status=HTTPStatus.NO_CONTENT)

        # NOTE: we're using the Django defaults for the cookie.
        # When left to default, the cookie should last "only as long as the client’s
        # browser session", though... I'm not sure how long that generally is :/
        # See: https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpResponse.set_cookie
        response.set_cookie(preference.cookie_name, value)
        return response
