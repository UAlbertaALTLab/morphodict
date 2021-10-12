"""
Django settings for cwdeng.

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
PRODUCTION_HOST = "itwiwina.altlab.dev"

DEFAULT_RUNSERVER_PORT = 8005

ALLOWED_HOSTS.append(PRODUCTION_HOST)

FST_TOOL_SAMPLES = [
    "kika-nîminaw",
    "kikaniminaw",
    "PV/ka+nîminîw+V+TA+Ind+2Sg+3SgO",
    "asiskîwithâkanihkîw",
    "asiskîwithâkanihkîw+V+AI+Ind+3Sg",
]

# Morphodict configuration

MORPHODICT_DICTIONARY_NAME = "itwîwina"

RELAXED_ANALYZER_FST_FILENAME = "analyzer-gt-desc.hfstol"
STRICT_ANALYZER_FST_FILENAME = RELAXED_ANALYZER_FST_FILENAME
STRICT_GENERATOR_FST_FILENAME = "generator-gt-norm.hfstol"

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "cr"

MORPHODICT_SOURCE_LANGUAGE = "cwd"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_SOURCE_LANGUAGE_NAME = "Woods Cree"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Cree"

MORPHODICT_LANGUAGE_ENDONYM = "nîhithawîwin"

# What orthographies -- writing systems -- are available
# Plains Cree has two primary orthographies:
#  - standard Roman orthography (e.g., nêhiyawêwin)
#  - syllabics (e.g., ᓀᐦᐃᔭᐍᐏᐣ)
#
# There may be further sub-variants of each orthography.
#
# Morphodict assumes that the `text` of all Wordform are written in the default
# orthography.
MORPHODICT_ORTHOGRAPHY = {
    # All entries in Wordform should be written in SRO (īōā).
    #
    # Reference: http://learncree.ca/ is a site made by LLRIB, and uses SRO with
    # macrons.
    #
    # That said, the current FST and database use circumflexes for the internal
    # orthography. We have to be careful to use macrons in the slugs.
    "default": "Latn-x-macron",
    "available": {
        "Latn-x-macron": {
            "name": "SRO (ēīōā)",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_macrons",
        },
        "Cans": {
            "name": "Syllabics",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_syllabics",
        },
        "CMRO": {"name": "CMRO", "converter": "cwdeng.app.orthography.to_cmro"},
    },
}
