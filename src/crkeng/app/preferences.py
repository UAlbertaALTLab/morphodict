"""
Preferences used in itwêwina, the Cree Intelligent Dictionary.
"""
from morphodict.lexicon.models import DictionarySource
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
class DictionarySource(Preference):
    """
    Which dictionaries should be included in the search results?
    """

    cookie_name = "dictionarysource"
    dictionary_sources = DictionarySource.objects.all()
    choices = {
        "All": "Show entries from all dictionary sources",
        "CW": "Wolvengrey, Arok, editor. Cree: Words. Regina, University of Regina Press, 2001",
        "MD": "Maskwacîs Dictionary. Maskwacîs, Maskwachees Cultural College, 1998.",
        "OS": "Starlight, Bruce, Gary Donovan, and Christopher Cox, editors. John Onespot and Edward Sapir: Collected Tsuut’ina Narratives and Linguistic Notes. Revised scholarly edition in preparation; 1922."
    }

    default = "All"
