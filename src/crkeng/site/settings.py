"""
Django settings for crkeng.

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
PRODUCTION_HOST = "itwewina.altlab.dev"

ALLOWED_HOSTS.append(PRODUCTION_HOST)

INSTALLED_APPS.insert(0, "crkeng.app")

FST_TOOL_SAMPLES = ["kika-nîminaw", "kikaniminaw", "PV/ka+nîminêw+V+TA+Ind+2Sg+3SgO"]

# Morphodict configuration

SHOW_DICT_SOURCE_SETTING = True

STRICT_GENERATOR_FST_FILENAME = "generator-gt-dict-norm.hfstol"
STRICT_ANALYZER_FST_FILENAME = "analyser-gt-dict-norm.hfstol"
RELAXED_ANALYZER_FST_FILENAME = "analyser-gt-dict-desc.hfstol"

MORPHODICT_DICTIONARY_NAME = "itwêwina"

MORPHODICT_SUPPORTS_AUTO_DEFINITIONS = True

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "cr"

MORPHODICT_SOURCE_LANGUAGE = "crk"
MORPHODICT_TARGET_LANGUAGE = "eng"

# MORPHODICT_PREVIEW_WARNING = False

MORPHODICT_SOURCE_LANGUAGE_NAME = "Plains Cree"
MORPHODICT_SOURCE_LANGUAGE_SHORT_NAME = "Cree"

MORPHODICT_LANGUAGE_ENDONYM = "nêhiyawêwin"

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
    # All entries in Wordform should be written in SRO (êîôâ)
    "default": "Latn-y",
    "available": {
        # 'Latn' is Okimāsis/Wolvegrey's SRO
        "Latn-y": {
            "name": "SRO (êîôâ) with y",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_y",
        },
        "Latn": {"name": "SRO (êîôâ) with ý"},
        "Latn-x-macron-y": {
            "name": "SRO (ēīōā) with y",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_macrons_with_y",
        },
        "Latn-x-macron": {
            "name": "SRO (ēīōā) with ý",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_macrons",
        },
        "Cans": {
            "name": "Syllabics",
            "converter": "CreeDictionary.CreeDictionary.orthography.to_syllabics",
        },
    },
}

# The order in which paradigm sizes will be presented to the user.
# The first size in this list is the "default".
# Make sure to exhaustively specify all size options available!
MORPHODICT_PARADIGM_SIZES = [
    # The most user-friendly size should be first:
    "basic",
    # Then, a more complete paradigm layout:
    "full",
    # Variants for linguists go here:
]

SPEECH_DB_EQ = ["maskwacis", "moswacihk"]
