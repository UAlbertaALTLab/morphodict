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


@attrs
class TitleRow:
    """
    A row containing only a title -- no inflections of table headers.
    """

    title = attrib(type=str)
    span = attrib(type=int)

    # Makes it so that the Django template can easily determine that this is a
    # title:
    is_title = True


class StaticCell:
    """
    A cell that undergoes no change in the when rendering a layout to a
    paradigm.
    """

    is_heading: bool = False
    is_label = False

    text: str

    def __str__(self) -> str:
        return self.text


@attrs(frozen=True)
class Label(StaticCell):
    """
    A title in the rendered paradigm.
    """

    is_label = True
    text = attrib(type=str)


@attrs(frozen=True)
class Heading(StaticCell):
    """
    A section header in the rendered paradigm.
    """

    is_heading = True
    text = attrib(type=str)


Cell = Union[str, StaticCell]

Row = Union[List[Cell], EmptyRowType, TitleRow]
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
        row = [determine_cell(cell) for cell in raw_row]

        has_content = False
        n_labels = 0
        last_label: str

        for cell in row:
            if isinstance(cell, Label):
                n_labels += 1
                last_label = cell.text
            elif cell != "":
                has_content = True

        if not has_content and n_labels == 0:
            layout.append(EmptyRow)
        elif not has_content and n_labels == 1:
            layout.append(TitleRow(last_label, span=len(row)))
        else:
            layout.append(row)

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
