"""
Preferences framework.

Allows for generic site-wide preferences stored in cookies.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Protocol

from django.http import HttpRequest
from django.template import Context
from django.utils.text import camel_case_to_spaces


@cache
def _registry():
    """
    Contains all Preference blueprints
    """
    return {}


class PreferenceDeclaration(Protocol):
    """
    What is required for a preference.
    """

    choices: dict[str, str]
    default: str


class PreferenceConfigurationError(Exception):
    """
    Raised when a preference is malconfigured.
    Client code should probably NOT catch this.
    """


def register_preference(declaration: PreferenceDeclaration, name=None):
    """
    Add a preference to the currently running site.
    """
    if name is None:
        if not isinstance(declaration, type):
            raise NotImplementedError
        if hasattr(declaration, "name"):
            name = declaration.name
        else:
            name = synthesize_name_from_class_name(declaration)

    # Validate the preference
    choices = declaration.choices
    default = declaration.default
    if default not in choices:
        raise PreferenceConfigurationError(
            f"Default does not exist in preference's choices: " f"{default=} {choices=}"
        )

    if hasattr(declaration, "cookie_name"):
        cookie_name = declaration.cookie_name
    else:
        cookie_name = name

    pref = Preference(name=name, choices=choices, default=default,
                       cookie_name=cookie_name)

    _registry()[name] = pref

    return  pref


def synthesize_name_from_class_name(cls: type):
    return camel_case_to_spaces(cls.__name__).replace(" ", "_")


@dataclass
class Preference:
    """
    A user preference, usually for the display of content on the website.
    """

    # Name used internally
    name: str

    # A mapping of all possible choices for this preference,
    # to user-readable labels.
    # {
    #     "internalname": "user-readable label"
    # }
    choices: dict[str, str]

    # Which one of the choices is the default
    default: str

    # Name used for the cookie
    cookie_name: str

    def current_value_from_template_context(self, context: Context) -> str:
        if hasattr(context, "request"):
            return self.current_value_from_request(context.request)
        else:
            return self.default

    def current_value_from_request(self, request: HttpRequest) -> str:
        return request.COOKIES.get(self.cookie_name, self.default)


def all_preferences():
    """
    Return the current preferences registered in this app.
    """
    return _registry().items()
