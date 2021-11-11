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
PRODUCTION_HOST = "itwewina.altlab.app"

ALLOWED_HOSTS.append(PRODUCTION_HOST)

INSTALLED_APPS.insert(0, "crkeng.app")

FST_TOOL_SAMPLES = ["kika-nîminaw", "kikaniminaw", "PV/ka+nîminêw+V+TA+Ind+2Sg+3SgO"]

# Morphodict configuration

STRICT_GENERATOR_FST_FILENAME = "crk-strict-generator.hfstol"
STRICT_ANALYZER_FST_FILENAME = "crk-strict-analyzer-for-dictionary.hfstol"
RELAXED_ANALYZER_FST_FILENAME = "crk-relaxed-analyzer-for-dictionary.hfstol"

MORPHODICT_DICTIONARY_NAME = "itwêwina"

MORPHODICT_SUPPORTS_AUTO_DEFINITIONS = True

# The ISO 639-1 code is used in the lang="" attributes in HTML.
MORPHODICT_ISO_639_1_CODE = "cr"

MORPHODICT_SOURCE_LANGUAGE = "crk"
MORPHODICT_TARGET_LANGUAGE = "eng"

MORPHODICT_PREVIEW_WARNING = False

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
    "default": "Latn",
    "available": {
        # 'Latn' is Okimāsis/Wolvegrey's SRO
        "Latn": {"name": "SRO (êîôâ)"},
        "Latn-x-macron": {
            "name": "SRO (ēīōā)",
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
