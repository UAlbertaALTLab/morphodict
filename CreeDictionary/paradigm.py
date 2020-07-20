#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Classes related to paradigms: both layouts and the filled paradigms.
"""

from string import Template
from typing import Iterable, List, Optional, Union

from attr import attrib, attrs

from typing_extensions import Literal

from utils.types import ConcatAnalysis


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


# frozen=False is a reminder that the inflection is default as None and generated later
# also inflection related info like inflection frequency in corpus
@attrs(frozen=False, auto_attribs=True, eq=False)
class InflectionCell:
    # the analysis of the inflection (with the lemma to be filled out)
    # It looks like for example "${lemma}+TAG+TAG+TAG", "TAG+${lemma}+TAG+TAG"
    # or it could be None in the case of an empty inflection cell
    analysis: Optional[Template]

    # the inflection to be generated
    inflection: Optional[str] = None

    # the frequency of the inflection in the corpus
    frequency: Optional[int] = None

    def is_empty(self):
        return self.analysis is None

    def generate_concat_analysis(self, lemma: str) -> Optional[ConcatAnalysis]:
        if self.analysis is not None:
            return ConcatAnalysis(self.analysis.substitute(lemma=lemma))
        return None

    def __eq__(self, other):
        return (
            isinstance(other, InflectionCell)
            and self.analysis.pattern == other.analysis.pattern
            and self.inflection == other.inflection
            and self.frequency == other.frequency
        )


Cell = Union[InflectionCell, StaticCell, Literal[""]]

Row = Union[List[Cell], EmptyRowType, TitleRow]

# TODO: Make a class for this?
Layout = List[Row]


def rows_to_layout(rows: Iterable[List[str]]) -> Layout:
    """
    Takes rows (e.g., from a TSV file), and creates a well-formatted layout
    file.
    """
    layout: Layout = []
    for raw_row in rows:
        row = determine_cells(raw_row)

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


def is_raw_row_heading(raw_row: List[str]) -> bool:
    """
    is the row a heading row that does not contain any inflection
    """
    for raw_cell in raw_row:
        if ":" in raw_cell:
            return True
    return False


def determine_cells(raw_row: List[str]) -> List[Cell]:
    """
    Parses the cell format and returns a list of cells, each of the cell is either:
        - a StaticCell (Heading/Label), which may have empty text
        - or an InflectionCell, either with analysis to fill out, or empty
    """
    cells: List[Cell] = []

    raw_row = [raw_cell.strip() for raw_cell in raw_row]

    is_heading_row = is_raw_row_heading(raw_row)

    for raw_cell in raw_row:
        raw_cell = raw_cell.strip()

        if raw_cell.startswith('"') and raw_cell.endswith('"'):
            # This will be something like:
            #   "Something is happening now"
            #   "Speech act participants"
            assert len(raw_cell) > 2
            cells.append(Label(raw_cell[1:-1]))
        elif raw_cell.startswith(":"):
            # This will be something like:
            #   : "ê-/kâ- word"
            #   : "ni-/ki- word"
            _colon, content, _empty = raw_cell.split('"')
            cells.append(Heading(content))
        elif raw_cell == "":
            # there are two kinds of empty cells
            # It could be in a "Heading row" which makes it a `Heading` type cell
            # or it could be in where an inflection should be, which makes it a InflectionCell
            if is_heading_row:
                cells.append(Heading(text=""))
            else:
                cells.append(InflectionCell(None))
        # it's an inflection cell
        else:
            # "{{ lemma }}" is a proprietary format
            cells.append(
                InflectionCell(Template(raw_cell.replace("{{ lemma }}", "${lemma}")))
            )
    return cells
