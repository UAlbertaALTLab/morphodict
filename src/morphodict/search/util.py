from typing import Optional, TypeVar

from cree_sro_syllabics import syllabics2sro

T = TypeVar("T")


def first_non_none_value(*l: Optional[T], default: Optional[T] = None) -> T:
    """
    Return the first item in the iterable that is not None.

    Handy for selecting the first set value from a bunch of `Optional`s. A
    default value may also be explicitly specified.

    >>> first_non_none_value('a', 'b')
    'a'
    >>> first_non_none_value(None, False, True)
    False
    >>> first_non_none_value(None, None, None, default='b')
    'b'
    """
    try:
        return next(a for a in l if a is not None)
    except StopIteration:
        if default is not None:
            return default
        raise Exception("only None values were provided")


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
