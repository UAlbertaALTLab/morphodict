import re
from typing import List, Optional, Tuple

from CreeDictionary.utils.enums import WordClass
from CreeDictionary.utils.types import FSTLemma, FSTTag

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


def extract_lemma(analysis: str) -> Optional[FSTLemma]:
    res = re.search(analysis_pattern, analysis)

    if res is None:
        # Cannot find word class
        return None

    assert (
        res.group("category") is not None
    ), f"failed to capture word class in analysis: {analysis}"

    end = res.span("category")[0]
    cursor = end - 1

    # Search for prefix tag(s), if they exist
    while cursor > 0 and analysis[cursor] != "+":
        cursor -= 1
    # Nudge the cursor to start where the lemma starts
    if analysis[cursor] == "+":
        cursor += 1

    return FSTLemma(analysis[cursor:end])


def extract_lemma_text_and_word_class(
    analysis: str,
) -> Optional[Tuple[FSTLemma, WordClass]]:
    """
    less overhead than calling `extract_lemma` and `extract_wc` separately
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:

        group = res.group("category")
        if group:
            end = res.span("category")[0]
            # print(res.groups())
            cursor = end - 1

            while cursor > 0 and analysis[cursor] != "+":
                cursor -= 1
            if analysis[cursor] == "+":
                cursor += 1

            lemma = analysis[cursor:end]

            if group.startswith("+Num"):  # special case
                group = group[4:]
            inflection_category = WordClass(group.replace("+", "").upper())

            return FSTLemma(lemma), inflection_category

        else:
            return None
    else:
        return None


def extract_word_class(analysis: str) -> Optional[WordClass]:
    """
    :param analysis: in the form of 'a+VAI+b+c'
    :return: None if extraction fails
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:
        group = res.group("category")

        if group:
            if group.startswith("+Num"):  # special case
                group = group[4:]
            return WordClass(group.replace("+", "").upper())
        else:
            return None
    else:
        return None
