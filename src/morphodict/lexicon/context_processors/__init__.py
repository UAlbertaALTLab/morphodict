from django.conf import settings


def language_pair(request):
    return {
        "LANGUAGE_PAIR": getattr(settings, "MORPHODICT_SOURCE_LANGUAGE", "???")
        + getattr(settings, "MORPHODICT_TARGET_LANGUAGE", "???")
    }
