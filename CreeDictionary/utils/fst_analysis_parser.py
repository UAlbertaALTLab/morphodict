import csv
import re
from enum import IntEnum, auto
from pathlib import Path
from typing import Dict, Iterable, List, Optional, TextIO, Tuple, TypeVar, Union

from utils.enums import WordClass
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
    Given an FST tag a desired "LabelFriendliness", provides access to the
    relabellings, as written by the linguists (mostly Antti).

    Use the shortcuts:

        .linguistic_short[tag]  or .linguistic_short.get(tag, default)
        .linguistic_long[tag]   or .linguistic_long.get(tag, default)
        .english[tag]           or .english.get(tag, default)
        .cree[tag]              or .cree.get(tag, default)
        .emoji[tag]             or .emoji.get(tag, default)
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

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            key = (key,)
        return key in self._data

    @classmethod
    def from_tsv(cls, csvfile: TextIO) -> "Relabelling":
        res = {}
        reader = csv.reader(csvfile, delimiter="\t")
        for row in list(reader)[1:]:
            if not any(row):
                # Skip empty row
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
                tag_dict[LabelFriendliness.LINGUISTIC_SHORT] = Label(row[1])
                tag_dict[LabelFriendliness.LINGUISTIC_LONG] = Label(row[2])
                tag_dict[LabelFriendliness.ENGLISH] = Label(row[3])
                tag_dict[LabelFriendliness.NEHIYAWEWIN] = Label(row[4])
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
        self,
        data: Relabelling._DataStructure,
        label: LabelFriendliness,
    ):
        self._data = data
        self._friendliness = label

    def __getitem__(self, key: FSTTag) -> Optional[Label]:
        return self._data[(key,)][self._friendliness]

    def get(self, key: FSTTag, default: Default = None) -> Union[Label, Default, None]:
        """
        Get a relabelling for the given FST tag.
        """
        return self._data.get((key,), {}).get(self._friendliness, default)

    def get_longest(self, tags: Iterable[FSTTag]) -> Optional[Label]:
        """
        Get a relabelling for the longest prefix of the given tags.
        """
        _unmatched, label = self._get_longest(tags)
        return label

    def chunk(self, tags: Iterable[FSTTag]) -> Iterable[Tuple[FSTTag, ...]]:
        """
        Chunk FST Labels that match relabellings and yield the tags.
        """
        tag_set = tuple(tags)
        while tag_set:
            unmatched, _ = self._get_longest(tag_set)
            prefix_length = len(tag_set) - len(unmatched)
            if prefix_length == 0:
                # There was no relabelling found, but we can just return the first tag.
                prefix_length = 1

            yield tag_set[:prefix_length]
            tag_set = tag_set[prefix_length:]

    def get_full_relabelling(self, tags: Iterable[FSTTag]) -> List[Label]:
        """
        Relabels all tags, trying to match prefixes
        """

        labels = []
        tag_set = tuple(tags)
        while tag_set:
            unmatched, maybe_label = self._get_longest(tag_set)
            if maybe_label is None:
                # No relabelling available! Just return the tag itself
                # TODO: raise a warning?
                label = Label(tag_set[0])
                tag_set = tag_set[1:]
            else:
                assert len(unmatched) < len(tag_set)
                label = maybe_label
                tag_set = unmatched
            labels.append(label)

        return labels

    def _get_longest(
        self, tags: Iterable[FSTTag]
    ) -> Tuple[Tuple[FSTTag, ...], Optional[Label]]:
        """
        Returns the unmatched tags, and the relabelling of the matched tags from the
        prefix.

        Returns a tuple of all tags if no prefix matched.
        """

        # TODO: better algorithm than this. Probably a trie
        try_tags = tuple(tags)
        end = len(try_tags)
        while end > 0:
            try:
                entry = self._data[try_tags[:end]]
            except KeyError:
                end -= 1
            else:
                return try_tags[end:], entry[self._friendliness]

        return try_tags, None


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
