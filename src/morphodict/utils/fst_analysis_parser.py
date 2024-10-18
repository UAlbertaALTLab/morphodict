import re
from typing import List, Tuple

from morphodict.utils.types import FSTLemma, FSTTag

analysis_pattern = re.compile(
    r"(?P<category>\+N\+A(\+D(?=\+))?|\+N\+I(\+D(?=\+))?|\+V\+AI|\+V\+T[AI]|\+V\+II|(\+Num)?\+Ipc|\+Pron).*?$"
)

partition_pattern = re.compile(
    r"""
    ^
    (
       (?: # prefix tag, e.g., ‘PV/e+’
         # The Multichar_Symbols ending with + in crk-dict.lexc start with one
         # of the following:
         (?:PV|IC|1|2|3|Rdpl)
         [^+]* # more
         \+ # literal plus
        )*
    )
    ([^+]+) # lemma
    (
        (?:\+[^+]+)* # tag
    )
    $
    """,
    re.VERBOSE,
)


def partition_analysis(analysis: str) -> Tuple[List[FSTTag], FSTLemma, List[FSTTag]]:
    """
    :return: the tags before the lemma, the lemma itself, the tags after the lemma
    :raise ValueError: when the analysis is not parsable.

    >>> partition_analysis('PV/e+fakeword+N+I')
    (['PV/e'], 'fakeword', ['N', 'I'])
    >>> partition_analysis('fakeword+N+I')
    ([], 'fakeword', ['N', 'I'])
    >>> partition_analysis('PV/e+PV/ki+atamihêw+V+TA+Cnj+1Pl+2SgO')
    (['PV/e', 'PV/ki'], 'atamihêw', ['V', 'TA', 'Cnj', '1Pl', '2SgO'])
    """

    match = partition_pattern.match(analysis)
    if not match:
        raise ValueError(f"analysis not parsable: {analysis}")

    pre, lemma, post = match.groups()
    return (
        [FSTTag(t) for t in pre.split("+") if t],
        FSTLemma(lemma),
        [FSTTag(t) for t in post.split("+") if t],
    )
