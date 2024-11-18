"""
Django settings for blaeng.

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
PRODUCTION_HOST = "ipowahsin.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8011

INSTALLED_APPS.insert(0, "blaeng.app")

# Morphodict configuration

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "bla"

MORPHODICT_SOURCE_LANGUAGE = "bla"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_SOURCE_LANGUAGE_NAME = "Blackfoot"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Blackfoot"

MORPHODICT_LANGUAGE_ENDONYM = "Niitsi’powahsin"

MORPHODICT_DICTIONARY_NAME = "i’pówahsin"

RELAXED_ANALYZER_FST_FILENAME = "analyser-gt-dict-desc.hfstol"
STRICT_ANALYZER_FST_FILENAME = RELAXED_ANALYZER_FST_FILENAME
STRICT_GENERATOR_FST_FILENAME = "generator-gt-dict-norm.hfstol"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}
