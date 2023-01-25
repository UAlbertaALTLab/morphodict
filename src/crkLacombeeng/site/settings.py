"""
Django settings for crk-Lacombeeng.

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
PRODUCTION_HOST = "lacombe.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8016

INSTALLED_APPS.insert(0, "crk-Lacombeeng.app")

# Morphodict configuration
STRICT_GENERATOR_FST_FILENAME = "crk-strict-generator.hfstol"
STRICT_ANALYZER_FST_FILENAME = "crk-strict-analyzer-for-dictionary.hfstol"
RELAXED_ANALYZER_FST_FILENAME = "crk-relaxed-analyzer-for-dictionary.hfstol"

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "crk-Lacombe"

MORPHODICT_SOURCE_LANGUAGE = "crk-Lacombe"
MORPHODICT_TARGET_LANGUAGE = "eng"
MORPHODICT_LANGUAGE_ENDONYM = "nêhiyawêwin"
MORPHODICT_DICTIONARY_NAME = "Lacombe"
MORPHODICT_SOURCE_LANGUAGE_NAME = "Lacombe Cree"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}
