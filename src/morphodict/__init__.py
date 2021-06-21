from django.conf import settings


def morphodict_language_pair():
    return getattr(settings, "MORPHODICT_SOURCE_LANGUAGE", "???") + getattr(
        settings, "MORPHODICT_TARGET_LANGUAGE", "???"
    )
