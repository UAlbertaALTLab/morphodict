#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Classes related to paradigms: both layouts and the filled paradigms.
"""

import warnings
from typing import Iterable, List, Sequence, Union, overload

from attr import attrib, attrs

Row = Union["RowWithContent", "EmptyRowType"]
Table = List[Row]


class RowWithContent(Sequence[str]):
    """
    A row in the layout that can be filled in.

    For now, it acts like a list.
    """

    def __init__(self, cells: List[str]):
        self.cells = cells

    def __repr__(self) -> str:
        return f"RowWithContent({self.cells!r})"

    # TODO: implement .fill(x: Analyses)
    # TODO: implement .title : str

    # Make it act like a list, mostly for backwards-compatibility reasons:

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, slc: slice) -> List[str]:
        ...

    def __getitem__(self, idx: Union[slice, int]) -> Union[str, List[str]]:
        return self.cells[idx]

    def __eq__(self, other) -> bool:
        if isinstance(other, list):
            warnings.warn(
                "Comparing with a list kept only for backwards compatibility reasons.",
                DeprecationWarning,
            )
            return self.cells == other
        elif isinstance(other, RowWithContent):
            return self.cells == other.cells
        else:
            return False

    def __iter__(self):
        return iter(self.cells)

    def __len__(self) -> int:
        return len(self.cells)


class EmptyRowType:
    """
    A completely empty row!
    """

    def __repr__(self) -> str:
        return "EmptyRow"


EmptyRow = EmptyRowType()
del EmptyRowType


@attrs(frozen=True)
class Label:
    """
    A title in the rendered paradigm.
    """

    is_label = True
    text = attrib(type=str)

    def __str__(self) -> str:
        return self.text


@attrs(frozen=True)
class Heading:
    """
    A section header in the rendered paradigm.
    """

    is_heading = True
    text = attrib(type=str)

    def __str__(self) -> str:
        return self.text


Cell = Union[str, Label, Heading]
# TODO: Make a class for this:
Layout = List[List[Cell]]


def rows_to_layout(rows: Iterable[List[str]]) -> Layout:
    """
    Takes rows (e.g., from a TSV file), and creates a well-formatted layout
    file.
    """
    return [[determine_cell(cell) for cell in row] for row in rows]


def determine_cell(raw_cell: str) -> Cell:
    # something like:
    #   "Something is happening now"
    #   "Speech act participants"
    if raw_cell.startswith('"') and raw_cell.endswith('"'):
        assert len(raw_cell) > 2
        return Label(raw_cell[1:-1])
    elif raw_cell.startswith(":"):
        _colon, content, _empty = raw_cell.split('"')
        return Heading(content)
    # TODO:
    # TODO: empty cells.
    else:
        return raw_cell
