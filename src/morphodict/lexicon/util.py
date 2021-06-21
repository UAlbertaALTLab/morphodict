import unicodedata
from unicodedata import normalize

EXTRA_REPLACEMENTS = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "Ø": "O"})


def strip_accents_for_search_lookups(s: str) -> str:
    """Remove accents from characters for approximate search"""
    return "".join(
        c for c in normalize("NFD", s) if unicodedata.combining(c) == 0
    ).translate(EXTRA_REPLACEMENTS)
