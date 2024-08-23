"""
Django settings for arpeng.

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
PRODUCTION_HOST = "nihiitono.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)
CSRF_TRUSTED_ORIGINS.append("https://" + PRODUCTION_HOST)

DEFAULT_RUNSERVER_PORT = 8007

INSTALLED_APPS.insert(0, "arpeng.app")

FST_TOOL_SAMPLES = [
    "nonoohowun",
    "[VERB][TA][ANIMATE-OBJECT][AFFIRMATIVE][PRESENT][IC]noohow[2SG-SUBJ][1SG-OBJ]",
]

# Morphodict configuration

MORPHODICT_DICTIONARY_NAME = "nihiitono"

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "arp"

MORPHODICT_SOURCE_LANGUAGE = "arp"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_ORTHOGRAPHY = {
    "default": "Latn",
    "available": {
        "Latn": {"name": "Latin"},
    },
}

MORPHODICT_TAG_STYLE = "Bracket"

MORPHODICT_ENABLE_FST_LEMMA_SUPPORT = True

MORPHODICT_SOURCE_LANGUAGE_NAME = "Arapaho"

MORPHODICT_LANGUAGE_ENDONYM = "Hinónoʼeitíít"
