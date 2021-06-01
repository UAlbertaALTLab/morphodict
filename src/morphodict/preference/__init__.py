"""
Preferences framework.

Allows for generic site-wide preferences stored in cookies.
"""
from __future__ import annotations

from functools import cache
from typing import Protocol, Type

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


def _is_direct_subclass_of_base_preference(cls: type) -> bool:
    """
    Returns True when this is a DIRECT subclass of BasePreference.
    """
    return cls.mro() == [cls, *BasePreference.mro()]


def register_preference(declaration: PreferenceDeclaration, name=None):
    """
    Add a preference to the currently running site.
    """
    if name is None:
        if not isinstance(declaration, type):
            raise NotImplementedError
        name = synthesize_name_from_class_name(declaration)

    # Validate the preference
    choices = declaration.choices
    default = declaration.default
    if default not in choices:
        raise PreferenceConfigurationError(
            f"Default does not exist in preference's choices: " f"{default=} {choices=}"
        )

    _registry()[name] = declaration


def synthesize_name_from_class_name(cls: type):
    return camel_case_to_spaces(cls.__name__).replace(" ", "_")


class BasePreference:
    """
    Keeps track of all Preference subclasses.
    """

    _has_seen_direct_subclass = False
    _subclasses: dict[str, Type[Preference]] = _registry()

    def __init_subclass__(cls, **kwargs):
        if _is_direct_subclass_of_base_preference(cls):
            # cls is the Preference class
            assert not BasePreference._has_seen_direct_subclass
            BasePreference._has_seen_direct_subclass = True
            assert len(BasePreference._subclasses) == 0
        else:
            register_preference(cls)

        super().__init_subclass__(**kwargs)


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

    @classmethod
    def current_value_from_template_context(cls, context: Context) -> str:
        if hasattr(context, "request"):
            return cls.current_value_from_request(context.request)
        else:
            return cls.default

    @classmethod
    def current_value_from_request(cls, request: HttpRequest) -> str:
        return request.COOKIES.get(cls.cookie_name, cls.default)


def all_preferences():
    """
    Return the current preferences registered in this app.
    """
    return _registry().items()
