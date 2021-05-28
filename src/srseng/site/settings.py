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
PRODUCTION_HOST = "srseng.altlab.dev"

DEFAULT_RUNSERVER_PORT = 8009

ALLOWED_HOSTS.append(PRODUCTION_HOST)

ROOT_URLCONF = "srseng.site.urls"

INSTALLED_APPS.insert(0, "srseng.app")

INSTALLED_APPS += ["srseng.dictimport"]

# Morphodict configuration

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "srs"

MORPHODICT_SOURCE_LANGUAGE = "srs"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}
