"""
Django settings for stoeng.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

from morphodict.site import base_dir_setup

BASE_DIR = Path(__file__).resolve().parent.parent

base_dir_setup.set_base_dir(BASE_DIR)

from morphodict.site.settings import *

# Where this application should be deployed:
PRODUCTION_HOST = "nakon-ie.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8018

INSTALLED_APPS.insert(0, "stoeng.app")

# Morphodict configuration

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "sto"

MORPHODICT_SOURCE_LANGUAGE = "sto"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_DICTIONARY_NAME = "nakón-i’e"
MORPHODICT_LANGUAGE_ENDONYM = "Nakoda"
MORPHODICT_SOURCE_LANGUAGE_NAME = "Stoney Nakoda"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Nakoda"

RELAXED_ANALYZER_FST_FILENAME = "analyser-gt-dict-norm.hfstol"
STRICT_ANALYZER_FST_FILENAME = RELAXED_ANALYZER_FST_FILENAME
STRICT_GENERATOR_FST_FILENAME = "generator-gt-dict-norm.hfstol"

FST_TOOL_SAMPLES = [ "yúda", "myudad" ]

# Without this, importjson by default will not attempt to add inflected definitions using phrase translation.
MORPHODICT_SUPPORTS_AUTO_DEFINITIONS = True
MORPHODICT_ENABLE_FST_LEMMA_SUPPORT = True
DEFAULT_TARGET_LANGUAGE_PHRASE_TAGS = ("+V",)

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}
