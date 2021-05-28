"""
Preferences framework.

Allows for generic site-wide preferences stored in cookies.
"""
from http import HTTPStatus
from typing import Type

from django.http import HttpResponse
from django.views import View


class Preference:
    cookie_name: str
    choices: list[str]
    default: str


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

    preference: Type[Preference]

    @property
    def cookie_name(self):
        return self.preference.cookie_name

    @property
    def choices(self):
        return self.preference.choices

    def post(self, request) -> HttpResponse:
        value = request.POST.get(self.cookie_name)

        # Tried to set to an unknown display mode
        if value not in self.preference.choices:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        if who_asked_us := request.headers.get("Referer"):
            # Force the browser to refresh the page that issued this request.
            response = HttpResponse(status=HTTPStatus.SEE_OTHER)
            response.headers["Location"] = who_asked_us
        else:
            # We don't know where to redirect, so send no content.
            # (also, this probably should never happen?)
            response = HttpResponse(status=HTTPStatus.NO_CONTENT)

        response.set_cookie(self.cookie_name, value)
        return response
