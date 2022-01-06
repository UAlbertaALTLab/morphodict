"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""
from django.conf import settings

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
        "source_language": settings.MORPHODICT_LANGUAGE_ENDONYM + " labels",
    }
    default = "english"


@register_preference
class AnimateEmoji(Preference):
    """
    Which emoji to use to substitute all animate emoji (awa words).
    """

    # Ensure the internal name and the cookie name (external name) are the same!
    name = "animate_emoji"
    cookie_name = name

    default = "iyiniw"  # the original itwêwina animate emoji
    choices = {
        "iyiniw": "🧑🏽",  # iyiniw (NA)/tastawiyiniw (NA)
        "granny": "👵🏽",  # kôhkom/*kokum (NDA)
        "grandpa": "👴🏽",  # môsom/*moshum (NDA)
        # Required by requester of this feature:
        "wolf": "🐺",  # mahihkan (NA)
        # Required for community partner
        "bear": "🐻",  # maskwa (NA)
        # Counter-intuitive awa word:
        "bread": "🍞",  # pahkwêsikan (NA)
        # Significant awa word:
        "star": "🌟",  # atâhk/acâhkos (NA)
        # I don't want to add too many options to start with, but more can always be
        # added in the future like:
        # - 🦬 paskwâwi-mostsos
        # - 🦫 amisk
    }


@register_preference
class DictionarySource(Preference):
    """
    Which dictionary source(s) should be displayed in the search results
    """

    # Ensure the internal name and the cookie name (external name) are the same!
    name = "dictionary_source"
    cookie_name = name

    default = "cw+md"
    choices = {
        "cw": "Show entries from the Cree: Words dictionary. Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001",
        "md": "Show entries from the Maskwacîs Dictionary. Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.",
        "cw+md": "Show entries from CW and MD (default)"
    }
