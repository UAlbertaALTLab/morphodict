from django.conf import settings

from morphodict import morphodict_language_pair

DICTIONARY_RESOURCE_DIR = settings.BASE_DIR / "resources" / "dictionary"

DEFAULT_IMPORTJSON_FILE = DICTIONARY_RESOURCE_DIR / (
    morphodict_language_pair() + "_dictionary.importjson"
)
