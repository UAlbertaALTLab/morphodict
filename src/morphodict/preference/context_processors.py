from __future__ import annotations

from typing import Union

from django.http import HttpRequest

from morphodict.preference import Preference, all_preferences


def preferences(request):
    """
    If this context processor is enabled, every `RequestContext` will contain this
    variable:

     - `preferences`, which allows you to access all preferences

    In the following examples, replace <preference> with the name of the desired
    preference in snake_case.

    Iterate over every choice with its label:

        {% for choice, label in preferences.<preference>.choices_with_labels }}

    Get the request's current choice (internal value) for a preference:

        {{ preferences.<preference>.current_choice }}

    Get the request's current choice (user-facing) label for a preference:

        {{ preference.<preference>.current_label }}
    """
    return {"preferences": _PreferenceContextProcessor(request)}


class _PreferenceContextProcessor:
    """
    Makes preferences available in the template context.
    """

    def __init__(self, request: HttpRequest):
        self._request = request
        self._preferences = dict(all_preferences())

    def __getattr__(self, name: str) -> _PreferenceInfo:
        if pref := self._preferences.get(name):
            return _PreferenceInfo(pref, self._request)
        raise AttributeError(name)


class _PreferenceInfo:
    """
    Exposes certain info about a Preference to the template context.
    """

    def __init__(self, preference: Preference, request: HttpRequest):
        self._preference = preference
        self._request = request

    @property
    def choices_with_labels(self):
        """
        Returns an iterable of (choice, label) pairs for the current preference.
        The pairs are returned in declaration order in the original Preference subclass.
        """
        return self._preference.choices.items()

    @property
    def current_choice(self) -> str:
        """
        Returns the current choice (internal value) for a preference, given the
        current request.
        """
        return self._preference.current_value_from_request(self._request)

    @property
    def current_label(self) -> Union[str, list[str]]:
        """
        Returns the current label (user-facing) for a preference, given the
        current request.
        """
        return self._preference.choices[self.current_choice]
