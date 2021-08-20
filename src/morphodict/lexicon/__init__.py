from pathlib import Path

from django.conf import settings

from morphodict import morphodict_language_pair

DICTIONARY_RESOURCE_DIR = settings.BASE_DIR / "resources" / "dictionary"

DEFAULT_FULL_IMPORTJSON_FILE = DICTIONARY_RESOURCE_DIR / (
    f"{morphodict_language_pair()}_dictionary.importjson"
)
DEFAULT_TEST_IMPORTJSON_FILE = DICTIONARY_RESOURCE_DIR / (
    f"{morphodict_language_pair()}_test_db.importjson"
)

DEFAULT_IMPORTJSON_FILE = (
    DEFAULT_TEST_IMPORTJSON_FILE
    if settings.USE_TEST_DB
    else DEFAULT_FULL_IMPORTJSON_FILE
)

MORPHODICT_LEXICON_RESOURCE_DIR = Path(__file__).parent / "resources"
