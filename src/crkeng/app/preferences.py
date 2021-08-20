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
class DictionarySourceCw(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "dictionary_source_cw"
    choices = {
        "yes": "Entries from the CW dictionary source will appear in your search results",
        "no": "Entries from the CW dictionary will be hidden in your search results",
        # "All": "Show entries from all dictionary sources",
        # "CW": "Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001",
        # "MD": "Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.",
        # "OS": "Starlight, Bruce, Gary Donovan, and Christopher Cox, editors. John Onespot and Edward Sapir: Collected Tsuut’ina Narratives and Linguistic Notes. Revised scholarly edition in preparation; 1922."
    }

    default = "yes"


@register_preference
class DictionarySourceMd(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "dictionary_source_md"
    choices = {
        "yes": "Entries from the MD dictionary source will appear in your search results",
        "no": "Entries from the MD dictionary will be hidden in your search results",
    }

    default = "yes"
