import unicodedata
from unicodedata import normalize

EXTRA_REPLACEMENTS = str.maketrans(
    {"ł": "l", "Ł": "L", "ɫ": "l", "Ɫ": "l", "ø": "o", "Ø": "O"}
)


def to_source_language_keyword(s: str) -> str:
    """Convert a source-language wordform to an indexable keyword

    Currently removes accents, and leading and trailing hyphens.

    There will be collisions but we could use edit distance to rank them.
    """
    s = s.lower()
    return (
        "".join(c for c in normalize("NFD", s) if unicodedata.combining(c) == 0)
        .translate(EXTRA_REPLACEMENTS)
        .strip("-")
    )
