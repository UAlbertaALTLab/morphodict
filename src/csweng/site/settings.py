"""
Django settings for csweng.

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
PRODUCTION_HOST = "ininimowin.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8020

INSTALLED_APPS.insert(0, "csweng.app")

# Morphodict configuration

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "csw"

MORPHODICT_SOURCE_LANGUAGE = "csw"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "SRO"},
        "Cans": {
            "name": "Syllabics",
            "converter": "morphodict.orthography.utils.to_syllabics",
        },
    },
}

MORPHODICT_DICTIONARY_NAME = "ininímowin"
MORPHODICT_SOURCE_LANGUAGE_NAME = "Swampy Cree"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Cree"
MORPHODICT_LANGUAGE_ENDONYM = "ininímowin"
MORPHODICT_CONTACT_EMAIL = "altlab+ininimowin@ualberta.ca"
MORPHODICT_CONTACT_FORM = ""
