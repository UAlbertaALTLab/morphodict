"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""
from django.conf import settings

from morphodict.preference import register_preference, Preference


# @register_preference
# class DisplayMode(Preference):
#     """
#     As of 2021-04-14, "mode" is a coarse mechanism for affecting the display; there are
#     plans for more fine-grained control over the display of, e.g., search results.
#     """
#
#     cookie_name = "mode"
#     choices = {
#         # Community-mode: uses emoji and hides inflectional class
#         "community": "Community mode",
#         # Linguist-mode: always displays inflectional class (e.g., VTA-1, NA-3, IPJ, etc.)
#         "linguistic": "Linguistic mode",
#     }
#     default = "community"


@register_preference
class DisplayMode(Preference):
    """
    What style labels should be used in the paradigm?
    """

    cookie_name = "display_mode"
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
    Which dictionaries should be included in the search results?
    """

    cookie_name = "dictionary_source"
    choices = {
        "cw": "Show entries from the Cree: Words dictionary. Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001",
        "md": "Show entries from the Maskwacîs Dictionary. Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.",
        "cw+md": "Show entries from CW and MD (default)",
    }

    default = "cw+md"


@register_preference
class ShowEmoji(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "show_emoji"
    choices = {
        "yes": "Show emojis with my entries (default)",
        "no": "Don't show emojis with my entries",
    }

    default = "yes"


@register_preference
class ParadigmAudio(Preference):
    """
    Should we show audio in the paradigms?
    """

    cookie_name = "paradigm_audio"
    choices = {
        "yes": "I would like to see audio in paradigm layouts",
        "no": "I do not want to see audio in paradigm layouts",
    }
    default = "no"
