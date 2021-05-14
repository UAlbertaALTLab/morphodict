### TODO FIXME TEMPORARY
# This really belongs in the dictionary database model processing code, not the
# webapp, but is being put here temporarily.
# https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/709

import re

_RE_UNWANTED_ENDING = re.compile(" (Also|Or|Animate|Inanimate).*")
_RE_PARENTHETICAL = re.compile(
    r"""
    \( # in round brackets
        (?! # docs: “Matches if ... doesn’t match next”
            (
                it/him
                |it
                |s\.o\.\ as
                |s\.t\.(\ as)?
            )
        )
        .*? # anything, but non-greedy
    \)

    | # or

    \[ # in square brackets:
        .*? # anything, but non-greedy
    \]
    """,
    re.VERBOSE,
)


def remove_parentheticals(text):
    text = _RE_UNWANTED_ENDING.sub("", text)
    text = _RE_PARENTHETICAL.sub("", text)
    text = text.strip()
    if text.endswith(";"):
        text = text[:-1]
    return text
