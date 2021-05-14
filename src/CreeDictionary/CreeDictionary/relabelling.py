from __future__ import annotations

import csv
from enum import IntEnum
from typing import Iterable, Optional, TextIO, Tuple, TypeVar, Union

from CreeDictionary.utils import shared_res_dir
from CreeDictionary.utils.types import FSTTag, Label

CRK_ALTERNATE_LABELS_FILE = shared_res_dir / "crk.altlabel.tsv"


class _LabelFriendliness(IntEnum):
    """
    Weird enum that I'm not sure should have ever existed.

    Values are assigned according to their corresponding column in crk.altlabel.tsv
    """

    LINGUISTIC_SHORT = 1
    LINGUISTIC_LONG = 2
    ENGLISH = 3
    NEHIYAWEWIN = 4
    EMOJI = 5


class Relabelling:
    """
    Given an FST tag, provides access to the relabellings, as written by the linguists
    (mostly Antti).

    Access as the following:

        .linguistic_short[tag]  or .linguistic_short.get(tag, default)
        .linguistic_long[tag]   or .linguistic_long.get(tag, default)
        .english[tag]           or .english.get(tag, default)
        .cree[tag]              or .cree.get(tag, default)
        .emoji[tag]             or .emoji.get(tag, default)
    """

    # This data structure is kind of a weird, but I'm keeping it for now.
    _DataStructure = dict[Tuple[FSTTag, ...], dict[_LabelFriendliness, Optional[Label]]]

    def __init__(self, data: _DataStructure) -> None:
        self._data = data

        self.linguistic_short = _RelabelFetcher(
            data, _LabelFriendliness.LINGUISTIC_SHORT
        )
        self.linguistic_long = _RelabelFetcher(data, _LabelFriendliness.LINGUISTIC_LONG)
        self.english = _RelabelFetcher(data, _LabelFriendliness.ENGLISH)
        self.cree = _RelabelFetcher(data, _LabelFriendliness.NEHIYAWEWIN)
        self.emoji = _RelabelFetcher(data, _LabelFriendliness.EMOJI)

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            key = (key,)
        return key in self._data

    @classmethod
    def from_tsv(cls, tsv_file: TextIO) -> Relabelling:
        res = {}
        reader = csv.reader(tsv_file, delimiter="\t")
        rows = iter(reader)

        # Skip header:
        next(rows)

        for row in rows:
            if not any(row):
                # Skip empty row
                continue

            tag_set = tuple(FSTTag(tag) for tag in row[0].split("+"))
            assert tag_set, f"Found a line with content, but no tag: {row!r}"

            tag_dict = {}
            for column_no in _LabelFriendliness:
                tag_dict[column_no] = _label_from_column_or_none(column_no, row)

            res[tag_set] = tag_dict

        return cls(res)


class _RelabelFetcher:
    """
    Makes accessing relabellings for a particular label friendliness easier.
    """

    def __init__(
        self,
        data: Relabelling._DataStructure,
        label: _LabelFriendliness,
    ):
        self._data = data
        self._friendliness = label

    def __getitem__(self, key: FSTTag) -> Optional[Label]:
        return self._data[(key,)][self._friendliness]

    def get(self, key: FSTTag, default: Optional[Label] = None) -> Optional[Label]:
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

    def chunk(self, tags: Iterable[FSTTag]) -> Iterable[tuple[FSTTag, ...]]:
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

    def get_full_relabelling(self, tags: Iterable[FSTTag]) -> list[Label]:
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
    ) -> tuple[tuple[FSTTag, ...], Optional[Label]]:
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


def _label_from_column_or_none(column_no: _LabelFriendliness, row) -> Optional[Label]:
    """
    Extract a non-empty label from row, else return none.
    """
    try:
        raw_label = row[column_no]
    except IndexError:
        # Some columns are empty.
        return None

    cleaned_label = raw_label.strip()
    if cleaned_label == "":
        return None

    return Label(cleaned_label)


def read_labels() -> Relabelling:
    with CRK_ALTERNATE_LABELS_FILE.open(encoding="UTF-8") as tsv_file:
        return Relabelling.from_tsv(tsv_file)


LABELS: Relabelling = read_labels()
