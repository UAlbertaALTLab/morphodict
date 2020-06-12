import csv
import re
from enum import IntEnum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, TextIO, Tuple, TypeVar, Union

from utils.enums import SimpleLexicalCategory
from utils.types import FSTLemma, FSTTag, Label

from .shared_res_dir import shared_res_dir

Default = TypeVar("Default")

analysis_pattern = re.compile(
    r"(?P<category>\+N\+A(\+D(?=\+))?|\+N\+I(\+D(?=\+))?|\+V\+AI|\+V\+T[AI]|\+V\+II|(\+Num)?\+Ipc|\+Pron).*?$"
)


class LabelFriendliness(IntEnum):
    LINGUISTIC_SHORT = auto()
    LINGUISTIC_LONG = auto()
    ENGLISH = auto()
    NEHIYAWEWIN = auto()
    EMOJI = auto()


class Relabelling:
    """
    Given an FST tag, and a "label friendliness", provides access to the
    relabellings, as written by the linguists (mostly Antti).

    Supports the dict API, for legacy reasons ¯\_(ツ)_/¯

    Preferred usage:

    Use the shortcuts:

        .linguistic_short[tag]  or .linguistic_short.get(tag, default)
        .linguistic_long[tag]   or .linguistic_long.get(tag, default)
        .english[tag]           or .english.get(tag, default)
        .cree[tag]              or .cree.get(tag, default)
        .emoji[tag]             or .emoji.get(tag, default)

    Try not to use this as a dictionary.
    """

    _DataStructure = Dict[Tuple[FSTTag, ...], Dict[LabelFriendliness, Optional[Label]]]

    def __init__(self, data: _DataStructure) -> None:
        self._data = data

        self.linguistic_short = _RelabelFetcher(
            data, LabelFriendliness.LINGUISTIC_SHORT
        )
        self.linguistic_long = _RelabelFetcher(data, LabelFriendliness.LINGUISTIC_LONG)
        self.english = _RelabelFetcher(data, LabelFriendliness.ENGLISH)
        self.cree = _RelabelFetcher(data, LabelFriendliness.NEHIYAWEWIN)
        self.emoji = _RelabelFetcher(data, LabelFriendliness.EMOJI)

    def get(self, key, optional=None):
        return self._data.get(key, optional)

    def __contains__(self, key: object) -> bool:
        # TODO: something with tuples?
        return (key,) in self._data

    @classmethod
    def from_tsv(cls, csvfile: TextIO) -> "Relabelling":
        res = {}
        reader = csv.reader(csvfile, delimiter="\t")
        for row in list(reader)[1:]:
            if not any(row):
                continue

            tag_set = tuple(FSTTag(tag) for tag in row[0].split("+"))
            assert tag_set, f"Found a line with content, but no tag: {row!r}"

            tag_dict: Dict[LabelFriendliness, Optional[Label]] = {
                LabelFriendliness.LINGUISTIC_SHORT: None,
                LabelFriendliness.LINGUISTIC_LONG: None,
                LabelFriendliness.ENGLISH: None,
                LabelFriendliness.NEHIYAWEWIN: None,
                LabelFriendliness.EMOJI: None,
            }

            try:
                short = row[1]
                tag_dict[LabelFriendliness.LINGUISTIC_SHORT] = Label(short)
                long = row[2]
                tag_dict[LabelFriendliness.LINGUISTIC_LONG] = Label(long)
                english = row[3]
                tag_dict[LabelFriendliness.ENGLISH] = Label(english)
                nihiyawewin = row[4]
                tag_dict[LabelFriendliness.NEHIYAWEWIN] = Label(nihiyawewin)
                tag_dict[LabelFriendliness.EMOJI] = Label(row[5])
            except IndexError:  # some of them do not have that many columns
                pass

            res[tag_set] = tag_dict

        return cls(res)


class _RelabelFetcher:
    """
    Makes accessing relabellings for a particular label friendliness easier.
    """

    def __init__(
        self, data: Relabelling._DataStructure, label: LabelFriendliness,
    ):
        self._data = data
        self._label = label

    def __getitem__(self, key: FSTTag) -> Optional[Label]:
        return self._data[(key,)][self._label]

    def get(self, key: FSTTag, default: Default = None) -> Union[Label, Default, None]:
        """
        Get a relabelling for the given FST tag.
        """
        return self._data.get((key,), {}).get(self._label, default)

    def get_longest(self, tags: Iterable[FSTTag]) -> Optional[Label]:
        """
        Get a relabelling for the longest prefix of the given tags.
        """

        # TODO: better algorithm than this. Probably a trie
        try_tags = tuple(tags)
        while try_tags:
            try:
                entry = self._data[try_tags]
            except KeyError:
                try_tags = try_tags[:-2]
            else:
                return entry[self._label]

        return None


def read_labels() -> Relabelling:
    with (shared_res_dir / "crk.altlabel.tsv").open(encoding="UTF-8") as csvfile:
        return Relabelling.from_tsv(csvfile)


LABELS: Relabelling = read_labels()


def partition_analysis(analysis: str) -> Tuple[List[FSTTag], FSTLemma, List[FSTTag]]:
    """
    :return: the tags before the lemma, the lemma itself, the tags after the lemma
    :raise ValueError: when the analysis is not parsable.

    >>> partition_analysis('PV/e+fakeword+N+I')
    (['PV/e'], 'fakeword', ['N', 'I'])
    >>> partition_analysis('fakeword+N+I')
    ([], 'fakeword', ['N', 'I'])
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:

        group = res.group("category")
        if group:
            end = res.span("category")[0]
            cursor = end - 1

            while cursor > 0 and analysis[cursor] != "+":
                cursor -= 1
            if analysis[cursor] == "+":
                cursor += 1

            return (
                [FSTTag(t) for t in analysis[: cursor - 1].split("+")]
                if cursor > 1
                else [],
                FSTLemma(analysis[cursor:end]),
                [FSTTag(t) for t in analysis[end + 1 :].split("+")],
            )
    raise ValueError(f"analysis not parsable: {analysis}")


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
    :return: None if extraction fails
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
