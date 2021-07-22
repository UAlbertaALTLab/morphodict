"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""

from morphodict.preference import register_preference, Preference


@register_preference
class DisplayMode(Preference):
    """
    As of 2021-04-14, "mode" is a coarse mechanism for affecting the display; there are
    plans for more fine-grained control over the display of, e.g., search results.
    """

    cookie_name = "mode"
    choices = {
        # Community-mode: uses emoji and hides inflectional class
        "community": "Community mode",
        # Linguist-mode: always displays inflectional class (e.g., VTA-1, NA-3, IPJ, etc.)
        "linguistic": "Linguistic mode",
    }
    default = "community"


@register_preference
class ParadigmLabel(Preference):
    """
    What style labels should be used in the paradigm?
    """

    cookie_name = "paradigmlabel"
    choices = {
        # Plain English labels; e.g., I → You (one), Something is happening now
        "english": "plain English labels",
        # (Short) linguistic labels; e.g., 1Sg → 2Sg, Present Tense
        "linguistic": "linguistic labels",
        # nêhiyawêwin labels; e.g., niya → kiya, mêkwâc
        "nehiyawewin": "nêhiyawêwin labels",
    }
    default = "english"
