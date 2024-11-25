"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""

from django.conf import settings

from morphodict.preference import register_preference, Preference


@register_preference
class DisplayMode(Preference):
    """
    What style labels should be used in the paradigm?
    """

    cookie_name = "display_mode"
    choices = {
        # Plain English labels; e.g., I → You (one), Something is happening now
        "english": "Plain English labels",
        # (Short) linguistic labels; e.g., 1Sg → 2Sg, Present Tense
        "linguistic": "Linguistic labels",
        # nêhiyawêwin labels; e.g., niya → kiya, mêkwâc
        "source_language": str(settings.MORPHODICT_LANGUAGE_ENDONYM) + " labels",
    }
    default = "english"