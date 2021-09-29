"""
Django settings for hdneng.

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
PRODUCTION_HOST = "guusaaw.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8010

INSTALLED_APPS.insert(0, "hdneng.app")

# Morphodict configuration

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "hdn"

MORPHODICT_SOURCE_LANGUAGE = "hdn"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_LANGUAGE_ENDONYM = "X̲aad Kíl"
MORPHODICT_DICTIONARY_NAME = "Gúusaaw"
MORPHODICT_SOURCE_LANGUAGE_NAME = "Northern Haida"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}
