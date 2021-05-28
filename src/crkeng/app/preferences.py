"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""

from morphodict.preference import Preference


class DisplayMode(Preference):
    """
    As of 2021-04-14, "mode" is a coarse mechanism for affecting the display; there are
    plans for more fine-grained control over the display of, e.g., search results.
    """

    cookie_name = "mode"
    choices = [
        # Community-mode: uses emoji and hides inflectional class
        "community",
        # Linguist-mode: always displays inflectional class (e.g., VTA-1, NA-3, IPJ, etc.)
        "linguistic",
    ]
    default = "community"


class ParadigmLabel(Preference):
    cookie_name = "paradigmlabel"
    choices = ["english", "linguistic", "nehiyawewin"]
    default = "english"
