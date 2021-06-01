from __future__ import annotations
from typing import Type

from morphodict.preference import all_preferences, Preference


def preferences(request):
    """
    Add this to the settings.py CONTEXT_PROCESSORS to be able to access preferences
    in templates.

    Usage:

        # settings.py
        CONTEXT_PROCESSORS = [
            "morphodict.preference.context_processors.preferences"
        ]

        # app/preferences.py
        from morphodict.preference import Preference

        class MyPreference(Preference):
            choices = ...
            default = ...

        # my-template.py
        {% for choice, label in preferences.my_preference.choices_with_labels %}
            <option value="{{ choice }}">{{ label }}</option>
        {% endfor %}
    """
    return {"preferences": _PreferenceContextProcessor()}


class _PreferenceContextProcessor:
    """
    Makes preferences available in the template context.
    """

    def __init__(self):
        self._preferences = dict(all_preferences())

    def __getattr__(self, name: str) -> _PreferenceInfo:
        if pref := self._preferences.get(name):
            return _PreferenceInfo(pref)
        raise AttributeError(name)


class _PreferenceInfo:
    """
    Exposes certain info about a Preference to the template context.
    """
    def __init__(self, preference: Type[Preference]):
        self._preference = preference

    @property
    def choices_with_labels(self):
        return self._preference.choices.items()