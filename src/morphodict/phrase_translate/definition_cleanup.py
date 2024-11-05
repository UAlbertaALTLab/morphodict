### TODO FIXME TEMPORARY
# This really belongs in the dictionary database model processing code, not the
# webapp, but is being put here temporarily.
# https://github.com/UAlbertaALTLab/morphodict/issues/709

import re

_RE_UNWANTED_ENDING = re.compile(" (Also|Or|Animate|Inanimate).*")

PARENTHESIZED_PART = r"""
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
"""

_RE_PARENTHETICAL = re.compile(
    rf"""
    
    # If the parenthesized part comes at the end of a sentence, remove the space
    # before it as well
    \s+
    {PARENTHESIZED_PART}
    (?=\.) # lookahead for literal period 
    
    | # or a standalone parenthesized expression

    {PARENTHESIZED_PART}   #

    | # or

    \[ # in square brackets:
        .*? # anything, but non-greedy
    \]
    """,
    re.VERBOSE,
)


def cleanup_target_definition_for_translation(text):
    text = _RE_UNWANTED_ENDING.sub("", text)
    text = _RE_PARENTHETICAL.sub("", text)
    text = text.strip()
    if text.endswith(";"):
        text = text[:-1]
    return text
