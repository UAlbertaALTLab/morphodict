from cree_sro_syllabics import syllabics2sro

from API.search.types import InternalForm


def to_internal_form(user_query: str) -> InternalForm:
    """
    Convert text to the internal form used by the database entries, tries, FSTs, etc.

    In itwêwina, the Plains Cree dictionary, this means SRO circumflexes.
    """
    return InternalForm(to_sro_circumflex(user_query))


def to_sro_circumflex(text: str) -> str:
    """
    Convert text to Plains Cree SRO with circumflexes (êîôâ).

    >>> to_sro_circumflex("tān'si")
    "tân'si"
    >>> to_sro_circumflex("ᑖᓂᓯ")
    'tânisi'
    """
    text = text.replace("ā", "â").replace("ē", "ê").replace("ī", "î").replace("ō", "ô")
    return syllabics2sro(text)
