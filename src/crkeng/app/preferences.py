"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""
from CreeDictionary.CreeDictionary.display_options import (
    DISPLAY_MODE_COOKIE,
    DISPLAY_MODES,
)
from morphodict.preference import Preference


class DisplayMode(Preference):
    cookie_name = DISPLAY_MODE_COOKIE
    choices = list(DISPLAY_MODES)
    default = "community"


class ParadigmLabel(Preference):
    cookie_name = "paradigmlabel"
    choices = ["english", "linguistic", "nehiyawewin"]
    default = "english"
