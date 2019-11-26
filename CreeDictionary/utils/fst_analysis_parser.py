import re
from os.path import dirname
from pathlib import Path
from typing import Iterable, Dict, Optional, Set, Pattern
from typing import Tuple

from constants import SimpleLexicalCategory, FSTLemma

inflection_category_to_pattern = (
    dict()
)  # type: Dict[SimpleLexicalCategory, Pattern[str]]

with open(Path(dirname(__file__)) / ".." / "res" / "lemma-tags.tsv") as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line:
            cells = line.split("\t")
            category = SimpleLexicalCategory(cells[0].upper())

            # IPC and Pron are special cases
            if (
                category is not SimpleLexicalCategory.IPC
                and category is not SimpleLexicalCategory.Pron
            ):
                inflection_category_to_pattern[category] = re.compile(
                    "[^+]+" + re.escape(cells[1].split("{{ lemma }}")[-1])
                )


# layout_class = re.match("(nad?|nid?|vai|vii|vt[ai]|ipc)", layout_name).groups()[0]


analysis_pattern = re.compile(
    r"(?P<category>\+N\+A(\+D)?|\+N\+I(\+D)?|\+V\+AI|\+V\+T[AI]|\+V\+II|(\+Num)?\+Ipc|\+Pron).*?$"
)


def extract_lemma(analysis: str) -> Optional[FSTLemma]:
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
            # print(cursor, end)
            return FSTLemma(analysis[cursor:end])
        else:
            return None
    else:
        return None


def extract_lemma_and_category(
    analysis: str,
) -> Optional[Tuple[FSTLemma, SimpleLexicalCategory]]:
    """
    less overhead than calling `extract_lemma` and `extract_simple_lc` separately
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
            inflection_category = SimpleLexicalCategory(group.replace("+", "").upper())

            return FSTLemma(lemma), inflection_category

        else:
            return None
    else:
        return None


def extract_simple_lc(analysis: str) -> Optional[SimpleLexicalCategory]:
    """
    :param analysis: in the form of 'a+VAI+b+c'
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:
        group = res.group("category")

        if group:
            if group.startswith("+Num"):  # special case
                group = group[4:]
            return SimpleLexicalCategory(group.replace("+", "").upper())
        else:
            return None
    else:
        return None
