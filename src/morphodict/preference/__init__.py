"""
Preferences framework.

Allows for generic site-wide preferences stored in cookies.
"""
from __future__ import annotations

from http import HTTPStatus
from typing import Type

from django.http import HttpResponse, HttpRequest
from django.template import Context
from django.utils.text import camel_case_to_spaces
from django.views import View


class PreferenceConfigurationError(Exception):
    """
    Raised when a preference is malconfigured.
    Client code should probably NOT catch this.
    """


class BasePreference:
    """
    Keeps track of all Preference subclasses.
    """

    # This is just here so that we can detect when Preference has been subclassed
    # from BasePreference.
    _base_subclass = None
    _subclasses: dict[str, Type[Preference]] = {}

    def __init_subclass__(cls, **kwargs):
        if BasePreference._base_subclass is None:
            BasePreference._base_subclass = cls
            assert len(BasePreference._subclasses) == 0
            assert cls.mro()[:2] == [cls, BasePreference]
        else:
            name = camel_case_to_spaces(cls.__name__).replace(" ", "_")
            BasePreference._subclasses[name] = cls

        super().__init_subclass__(**kwargs)

    @classmethod
    def current_value_from_template_context(cls: Type[Preference], context: Context) -> str:
        if hasattr(context, "request"):
            return cls.current_value_from_request(context.request)
        else:
            return cls.default

    @classmethod
    def current_value_from_request(cls: Type[Preference], request: HttpRequest) -> str:
        return request.COOKIES.get(cls.cookie_name, cls.default)


class Preference(BasePreference):
    """
    A user preference, usually for the display of content on the website.
    """

    cookie_name: str

    # A mapping of all possible choices for this preference,
    # to user-readable labels.
    # {
    #     "internalname": "user-readable label"
    # }
    choices: dict[str, str]

    # Which one of the choices is the default
    default: str

    def __init_subclass__(cls, **kwargs):
        choices = cls.choices
        default = cls.default
        if default not in choices:
            raise PreferenceConfigurationError(
                f"Default does not exist in preference's choices: " 
                f"{default=} {choices=}"
            )
        super().__init_subclass__(**kwargs)


def all_preferences():
    """
    Return the current preferences registered in this app.
    """
    return BasePreference._subclasses.items()


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
        # TODO: let preferences share ONE cookie
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

        # NOTE: we're using the Django defaults for the cookie.
        # When left to default, the cookie should last "only as long as the client’s
        # browser session", though... I'm not sure how long that generally is :/
        # See: https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.HttpResponse.set_cookie
        response.set_cookie(self.cookie_name, value)
        return response
