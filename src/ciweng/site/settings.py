"""
Django settings for ciweng.

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
PRODUCTION_HOST = "ciweng.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8019

INSTALLED_APPS.insert(0, "ciweng.app")

# Morphodict configuration

FST_TOOL_SAMPLES: list[str] = []

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "ciw"

MORPHODICT_SOURCE_LANGUAGE = "ciw"
MORPHODICT_TARGET_LANGUAGE = "eng"

STRICT_GENERATOR_FST_FILENAME = "generator-gt-norm-unweighted.hfstol"
STRICT_ANALYZER_FST_FILENAME = "analyser-gt-norm-unweighted.hfstol"
RELAXED_ANALYZER_FST_FILENAME = "analyser-gt-desc-unweighted.hfstol"

MORPHODICT_DICTIONARY_NAME = "ikidowinan"

MORPHODICT_SOURCE_LANGUAGE_NAME = "South-Western Ojibwe"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Ojibwe"

MORPHODICT_LANGUAGE_ENDONYM = "Anishnaabemowin"


MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}

MORPHODICT_PARADIGM_SIZES = ["basic", "full"]

SPEECH_DB_EQ = []
