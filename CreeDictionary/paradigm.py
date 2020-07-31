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
# inflection related info like inflection frequency is also generated later
@attrs(frozen=False, auto_attribs=True, eq=False, repr=False)
class InflectionCell:
    # the analysis of the inflection (with the lemma to be filled out)
    # It looks like for example "${lemma}+TAG+TAG+TAG", "TAG+${lemma}+TAG+TAG"
    analysis: Optional[Template] = None

    # the inflection to be generated
    inflection: Optional[str] = None

    # the frequency of the inflection in the corpus
    frequency: Optional[int] = None

    @property
    def has_analysis(self):
        return self.analysis is not None

    def __eq__(self, other) -> bool:
        # N.B., string.Template needs to be checked directly :/
        return isinstance(other, InflectionCell) and (
            (
                self.analysis is not None
                and other.analysis is not None
                and self.analysis.template == other.analysis.template
                and self.inflection == other.inflection
                and self.frequency == other.frequency
            )
            or (self.analysis is None and other.analysis is None)
        )

    def __repr__(self) -> str:
        if self.inflection or self.frequency and self.analysis is None:
            return super().__repr__()
        return f"{type(self).__name__}(analysis=Template({self.analysis.template!r})"

    def create_concat_analysis(self, lemma: str) -> ConcatAnalysis:
        """
        Fills in the analysis. Useful if you want to inflect this cell.

        >>> cell = InflectionCell.from_raw_nds_cell("{{ lemma }}+V+II+Ind+3Sg")
        >>> cell.create_concat_analysis("mispon")
        'mispon+V+II+Ind+3Sg'
        """
        assert self.analysis is not None

        return ConcatAnalysis(self.analysis.substitute(lemma=lemma))

    @classmethod
    def from_raw_nds_cell(cls, raw_cell: str) -> "InflectionCell":
        """
        Generates an InflectionCell from a NDS-style (legacy) template format.
        """
        return cls(Template(raw_cell.replace("{{ lemma }}", "${lemma}")))


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


def does_raw_row_has_row_header(raw_row: List[str]) -> bool:
    """
    does the row host inflection or not?
    """

    # we check if the row has a "left aligned heading"

    for i, raw_cell in enumerate(raw_row):

        if (
            raw_cell.startswith('"')
            and raw_cell.endswith('"')
            or raw_cell.startswith(":")
        ):
            return i == 0

    return False


def determine_cells(raw_row: List[str]) -> List[Cell]:
    has_row_header = does_raw_row_has_row_header(raw_row=raw_row)
    cells: List[Cell] = []

    for raw_cell in raw_row:
        cell: Cell

        if raw_cell.startswith('"') and raw_cell.endswith('"'):
            # This will be something like:
            #   "Something is happening now"
            #   "Speech act participants"
            assert len(raw_cell) > 2
            cell = Label(raw_cell[1:-1])
        elif raw_cell.startswith(":"):
            # This will be something like:
            #   : "ê-/kâ- word"
            #   : "ni-/ki- word"
            _colon, content, _empty = raw_cell.split('"')
            cell = Heading(content)
        else:
            raw_cell = raw_cell.strip()
            if raw_cell == "":
                if has_row_header:
                    cell = InflectionCell()
                else:
                    cell = ""
            else:
                # "{{ lemma }}" is a proprietary format
                cell = InflectionCell.from_raw_nds_cell(raw_cell)

        cells.append(cell)
    return cells
