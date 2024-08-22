from django.conf import settings
from django.core.checks import Error, register
from typing import Optional

class MorphodictSentinel:
    pass

_MORPHODICT_REQUIRED_SETTING_SENTINEL = MorphodictSentinel()

RequiredString = str | MorphodictSentinel


@register()
def check_settings(**kwargs):
    errors = []

    # borrowed from what django diffsettings command does
    assert settings.configured
    for key in dir(settings._wrapped):
        if not key.startswith("MORPHODICT_"):
            continue
        value = getattr(settings, key)
        if value == _MORPHODICT_REQUIRED_SETTING_SENTINEL:
            errors.append(
                Error(
                    f"Required morphodict setting {key} has not been configured.",
                    obj="check_settings",
                )
            )

    return errors
