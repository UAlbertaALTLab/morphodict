import re
from os.path import dirname
from pathlib import Path
from typing import Iterable, Dict, Optional, Set, Pattern
from typing import Tuple

from constants import SimpleLexicalCategory

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


def extract_lemma(analysis: str) -> Optional[str]:
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
            return analysis[cursor:end]
        else:
            return None
    else:
        return None


def extract_lemma_and_category(
    analysis: str,
) -> Optional[Tuple[str, SimpleLexicalCategory]]:
    """
    faster than calling `extract_lemma` and `extract_category` separately
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

            return lemma, inflection_category

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


def identify_lemma_analysis(analyses: Iterable[str]) -> Set[str]:
    """
    An example:

    for cree wâpi-maskwa, hfstol gives the below analyses:

    ['wâpi-maskwa+N+A+Obv', 'wâpi-maskwa+N+A+Sg']

    both inflections look the same as the lemma, but which is the preference for a lemma?
    this function returns the preferred lemma analyses according to res/lemma-tags.tsv

    For Pronouns and IPCs, as lemma-tags.tsv do not specify, this function basically returns the analyses as is.

    :raise ValueError if an analysis can not be understood
    """
    possible_analyses = set()

    for analysis in analyses:
        cat = extract_simple_lc(analysis)
        if cat is None:
            raise ValueError(
                f"Can not recognize the category of fst analysis {analysis}"
            )
        if cat is SimpleLexicalCategory.Pron:
            if "+Pron" in analysis:
                possible_analyses.add(analysis)
        elif cat is SimpleLexicalCategory.IPC:
            # +Num+IPC is a specially case. They are frequently used numbers and they are not lemmas
            if "+Ipc" in analysis and not analysis.endswith("+Num+Ipc"):
                possible_analyses.add(analysis)
        else:
            pattern = inflection_category_to_pattern[cat]
            if re.fullmatch(pattern, analysis):

                possible_analyses.add(analysis)

    return possible_analyses
