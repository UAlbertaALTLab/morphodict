from django.conf import settings


def morphodict_settings(request):
    exported_keys = [
        "MORPHODICT_PREVIEW_WARNING",
        "MORPHODICT_SOURCE_LANGUAGE_NAME",
        "MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME",
        "MORPHODICT_DICTIONARY_NAME",
        "MORPHODICT_ORTHOGRAPHY",
    ]

    return {k: getattr(settings, k) for k in exported_keys}
