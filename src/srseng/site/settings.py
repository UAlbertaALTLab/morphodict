"""
Django settings for srseng.

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
PRODUCTION_HOST = "gunaha.altlab.dev"

DEFAULT_RUNSERVER_PORT = 8009

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

INSTALLED_APPS.insert(0, "srseng.app")

INSTALLED_APPS += []

FST_TOOL_SAMPLES = ["istsiy", "itsiy+V+I+Ipfv+SbjSg1"]

# Morphodict configuration

MORPHODICT_DICTIONARY_NAME = "Gunáhà"

STRICT_ANALYZER_FST_FILENAME = "analyser-gt-norm.hfstol"
RELAXED_ANALYZER_FST_FILENAME = "analyser-gt-desc.hfstol"
STRICT_GENERATOR_FST_FILENAME = "generator-gt-norm.hfstol"

# The ISO 639-3 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "srs"

MORPHODICT_SOURCE_LANGUAGE = "srs"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_SOURCE_LANGUAGE_NAME = "Tsuut’ina"
MORPHODICT_LANGUAGE_ENDONYM = "Tsúut'ínà"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}

SPEECH_DB_EQ = ["tsuutina"]

MORPHODICT_REQUIRES_LOGIN_IN_GROUP = "gunaha"
