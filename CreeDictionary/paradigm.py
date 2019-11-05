#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Classes related to paradigms: both layouts and the filled paradigms.
"""

import warnings
from typing import Iterable, List, Sequence, Union, overload

from attr import attrib, attrs


class EmptyRowType:
    """
    A completely empty row!
    """

    # Do a bunch of stuff to make this an empty row.
    _instance: "EmptyRowType"

    def __new__(cls) -> "EmptyRowType":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "EmptyRowType"

    def __deepcopy__(self, _memo) -> "EmptyRowType":
        return self

    def __copy__(self) -> "EmptyRowType":
        return self

    def __reduce__(self):
        return (EmptyRowType, ())


EmptyRow = EmptyRowType()


class StaticCell:
    """
    A cell that undergoes no change in the when rendering a layout to a
    paradigm.
    """

    is_heading: bool = False
    is_label = False


@attrs(frozen=True)
class Label(StaticCell):
    """
    A title in the rendered paradigm.
    """

    is_label = True
    text = attrib(type=str)

    def __str__(self) -> str:
        return self.text


@attrs(frozen=True)
class Heading(StaticCell):
    """
    A section header in the rendered paradigm.
    """

    is_heading = True
    text = attrib(type=str)

    def __str__(self) -> str:
        return self.text


Cell = Union[str, StaticCell]

Row = Union[List[Cell], EmptyRowType]
# TODO: delete this type:
Table = List[Row]

# TODO: Make a class for this?
Layout = List[Row]


def rows_to_layout(rows: Iterable[List[str]]) -> Layout:
    """
    Takes rows (e.g., from a TSV file), and creates a well-formatted layout
    file.
    """
    layout: Layout = []
    for raw_row in rows:
        if all(cell == "" for cell in raw_row):
            layout.append(EmptyRow)
        else:
            layout.append([determine_cell(cell) for cell in raw_row])

    return layout


def determine_cell(raw_cell: str) -> Cell:
    """
    Parses the cell format and returns either:
        - a StaticCel
        - an empty string (empty cell)
        - or a string (analysis to fill out)
    """
    if raw_cell.startswith('"') and raw_cell.endswith('"'):
        # This will be something like:
        #   "Something is happening now"
        #   "Speech act participants"
        assert len(raw_cell) > 2
        return Label(raw_cell[1:-1])
    elif raw_cell.startswith(":"):
        # This will be something like:
        #   : "ê-/kâ- word"
        #   : "ni-/ki- word"
        _colon, content, _empty = raw_cell.split('"')
        return Heading(content)
    else:
        return raw_cell
