"""
Provides all classes for pane-based paradigms.
"""

from __future__ import annotations

import logging
import re
import string
import urllib
import requests
from itertools import zip_longest
from typing import Collection, Iterable, Mapping, Optional, Sequence, TextIO

from more_itertools import ilen, one

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """
    Raised when there's an issue in parsing paradigm layouts.
    """


class ParadigmGenerationError(Exception):
    """
    Raised when there's some issue with generating/filling a paradigm.
    """


class ParadigmIsNotStaticError(Exception):
    """
    Raised when calling .as_static_paradigm() on a layout with unfilled
    placeholders (i.e., on a dynamic paradigm).
    """


class Paradigm:
    """
    A paradigm is intended to display a collection of wordforms related to a single
    lexeme, or a table of related wordforms.

    A paradigm in this project is composed of multiple **panes**. Each pane itself is a
    table, organized by **rows**, and then each row contains **cells**.
    """

    def __init__(self, panes: Iterable[Pane]):
        self._panes = tuple(panes)

    @property
    def panes(self) -> Iterable[Pane]:
        yield from self._panes

    @property
    def max_num_columns(self):
        """
        How many columns are necessary for this entire paradigm?
        """
        return max(pane.num_columns for pane in self.panes)

    def contains_wordform(self, wordform: str) -> bool:
        """
        True if the wordform is found ANYWHERE in the paradigm.
        """
        return any(pane.contains_wordform(wordform) for pane in self.panes)


class ParadigmLayout(Paradigm):
    """
    Layout for a particular word class. The layout contains placeholders
    (InflectionTemplate) that can be filled at runtime to generate a paradigm that
    can be rendered and shown to the user.
    """

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        for pane in self.panes:
            yield from pane.inflection_cells

    @classmethod
    def load(cls, layout_file: TextIO) -> ParadigmLayout:
        """
        Load a paradigm layout from a file.
        """
        return cls.loads(layout_file.read())

    @classmethod
    def loads(cls, text: str) -> ParadigmLayout:
        """
        Load a ParadigmLayout from a string.
        """
        lines = text.splitlines(keepends=False)

        pane_lines: list[list[str]] = [[]]
        for line in lines:
            if line.strip() == "":
                # empty line; start a new pane
                pane_lines.append([])
            else:
                # add line to current pane
                pane_lines[-1].append(line)

        pane_strs = ["\n".join(lines) for lines in pane_lines if len(lines) > 0]

        panes = [Pane.parse(p) for p in pane_strs if p.strip()]
        return ParadigmLayout(panes)

    def dumps(self):
        """
        Export the layout as a string. This string can be by .loads().
        """

        pane_text = []
        num_columns = self.max_num_columns
        for pane in self.panes:
            pane_text.append(pane.dumps(require_num_columns=num_columns))

        tabs = "\t" * (num_columns - 1)
        empty_line = f"\n{tabs}\n"

        return empty_line.join(pane_text)

    def generate_fst_analyses(self, lemma: str) -> dict[str, str]:
        """
        Generates a dictionary mapping analysis templates to analyses substituted with
        the given lemma.
        """
        return {
            inflection.analysis_template: inflection.as_analysis(lemma)
            for inflection in self.inflection_cells
        }

    def fill(self, forms: Mapping[str, Collection[str]]) -> Paradigm:
        """
        Given a mapping from analysis to a collection of wordforms, returns a
        paradigm with all its InflectionTemplate cells replaced with WordformCells.
        """
        return Paradigm(pane.fill(forms) for pane in self.panes)

    def as_static_paradigm(self) -> Paradigm:
        """
        Returns a Paradigm that can be rendered without having to explicitly fill it.

        :raises ParadigmIsNotStaticError: when called on a dynamic paradigm
        """
        if ilen(self.inflection_cells) > 0:
            raise ParadigmIsNotStaticError(
                "not a static paradigm; contains " "inflection templates"
            )
        return self.fill({})

    def __str__(self):
        return self.dumps()


class Pane:
    """
    A self-contained table from the full paradigm.

    A pane contains a number of rows.
    """

    def __init__(self, rows: Iterable[Row]):
        self._rows = tuple(rows)

    @property
    def header(self) -> Optional[HeaderRow]:
        first_row = self._rows[0]
        if isinstance(first_row, HeaderRow):
            return first_row
        return None

    @property
    def num_columns(self) -> int:
        return max(row.num_cells for row in self.rows)

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        for row in self.rows:
            yield from row.inflection_cells

    @property
    def rows(self) -> Iterable[Row]:
        yield from self._rows

    @property
    def tr_rows(self) -> Iterable[Row]:
        """
        Yields rows needed in the HTML model. All rows of a compound row are yielded
        individually.
        """
        for row in self._rows:
            if isinstance(row, CompoundRow):
                yield from row.subrows
            else:
                yield row

    def dumps(self, require_num_columns: Optional[int] = None) -> str:
        """
        Returns a string representation that can be parsed again.
        :param require_num_columns: if given, the pane must have at least this many columns.
                                    Rows are padded with empty cells at the end.
        """
        return "\n".join(row.dumps(require_num_columns) for row in self.rows)

    def __str__(self):
        return self.dumps()

    def __eq__(self, other) -> bool:
        if isinstance(other, Pane):
            return self._rows == other._rows
        return False

    def __repr__(self):
        name = type(self).__qualname__
        rows = ", ".join(repr(row) for row in self.rows)
        return f"{name}([{rows}])"

    @classmethod
    def parse(cls, text: str) -> Pane:
        lines = text.splitlines()

        if len(lines) == 0:
            raise ParseError("Not enough lines in pane")

        return Pane(ContentRow.parse(line) for line in lines)

    def contains_wordform(self, wordform: str) -> bool:
        return any(row.contains_wordform(wordform) for row in self.rows)

    def fill(self, forms: Mapping[str, Collection[str]]) -> Pane:
        return Pane(row.fill(forms) for row in self.rows)


class Row:
    is_header: bool
    has_content: bool
    num_cells: int

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        # subclasses MUST implement this somehow
        raise NotImplementedError

    @property
    def cells(self) -> Iterable[Cell]:
        # subclasses MUST implement this somehow
        raise NotImplementedError

    def dumps(self, require_num_columns: Optional[int] = None) -> str:
        """
        Returns a string representation of the row that can be parsed again.
        :param require_num_columns: if given, the row must have at least this many columns.
                                    The row is padded with empty cells at the end.
        """

        row_as_string = str(self)
        if require_num_columns is None:
            return row_as_string

        if require_num_columns < 1:
            raise ValueError("must require at least one column")

        # Figure out how many tabs we need to add to the end.
        total_tabs = require_num_columns - 1
        tabs_present = row_as_string.count("\t")
        tabs_left = max(total_tabs - tabs_present, 0)

        return row_as_string + "\t" * tabs_left

    def contains_wordform(self, wordform: str) -> bool:
        raise NotImplementedError

    def fill(self, forms: Mapping[str, Collection[str]]) -> Row:
        if not self.has_content:
            # Just labels; can return ourselves verbatim
            return self
        # Subclass must override this (i.e., ContentRow)
        raise NotImplementedError

    @staticmethod
    def parse(text: str) -> Row:
        if text.startswith("# "):
            return HeaderRow.parse(text)

        cell_texts = text.rstrip("\n").split("\t")
        # Remove empty cells from the end.
        while cell_texts:
            if cell_texts[-1].strip() != "":
                break
            cell_texts.pop()

        if len(cell_texts) == 0:
            # This would mean the line was empty, but empty lines in a paradigm file
            # are used as pane separators.
            # If we got here from ParadigmLayout.parse(), something terrible has gone
            # wrong.
            raise ParseError("Refusing to parse empty row")

        return ContentRow(Cell.parse(t) for t in cell_texts)


class ContentRow(Row):
    """
    A single row from a pane. Rows contain cells.
    """

    is_header = False
    has_content = True

    def __init__(self, cells: Iterable[Cell]):
        self._cells = tuple(cells)

    @property
    def cells(self):
        yield from self._cells

    @property
    def num_cells(self):
        return len(self._cells)

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        return (c for c in self.cells if isinstance(c, InflectionTemplate))

    def contains_wordform(self, wordform: str) -> bool:
        return any(cell.contains_wordform(wordform) for cell in self.cells)

    def fill(self, forms: Mapping[str, Collection[str]]) -> ContentRow | CompoundRow:
        """
        Fills the column and may return a ContentRow or a CompoundRow (a composition
        of ContentRows.
        """

        # Fill each **column**, then figure out if we need to make a compound row
        columns = n_empty_lists(self.num_cells)
        for index, cell in enumerate(self.cells):
            columns[index].extend(cell.fill(forms))

        num_rows_needed = max(len(c) for c in columns)
        assert num_rows_needed > 0
        if num_rows_needed == 1:
            # A row with all columns having a single cell:
            return ContentRow(one(cells) for cells in columns)

        # Create compound rows
        rows = []
        for row_num in range(num_rows_needed):
            cells = [cell_if_exists_or_no_output(col, row_num) for col in columns]
            cells = [adjust_row_span(cell, num_rows_needed) for cell in cells]
            rows.append(ContentRow(cells))
        return CompoundRow(rows)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ContentRow):
            return False
        return all(a == b for a, b in zip_longest(self.cells, other.cells))

    def __str__(self):
        try:
            return "\t".join(str(cell[0]) for cell in self.cells)
        except TypeError as e:
            return "\t".join(str(cell) for cell in self.cells)

    def __repr__(self):
        name = type(self).__qualname__
        cells_repr = ", ".join(repr(cell) for cell in self.cells)
        return f"{name}([{cells_repr}])"


class HeaderRow(Row):
    """
    A row that acts as a header for the rest of the pane.
    """

    prefix = "#"
    is_header = True
    has_content = False
    num_cells = 0

    def __init__(self, tags):
        super().__init__()
        self._tags = tuple(tags)

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        # a header, by definition, has no inflections.
        return ()

    @property
    def fst_tags(self) -> tuple[str, ...]:
        return self._tags

    def __eq__(self, other) -> bool:
        if isinstance(other, HeaderRow):
            return self._tags == other._tags
        return False

    def __str__(self):
        return " ".join(f"{self.prefix} {tag}" for tag in self._tags)

    def __repr__(self):
        name = type(self).__qualname__
        cells_repr = ", ".join(repr(cell) for cell in self._tags)
        return f"{name}([{cells_repr}])"

    def contains_wordform(self, wordform: str) -> bool:
        """
        A header **never** contains a wordform, so this always returns False.
        """
        return False

    @classmethod
    def parse(cls, text: str) -> HeaderRow:
        if not text.startswith(cls.prefix):
            raise ParseError("Not a header row: {text!r}")

        text = text.rstrip()
        return HeaderRow(parse_label(text, prefix=cls.prefix))


class CompoundRow(Row):
    """
    Contains multiple filled content rows.
    """

    is_header = False
    has_content = True

    def __init__(self, rows: Iterable[ContentRow]):
        self._rows = tuple(rows)

    @property
    def cells(self) -> Iterable[Cell]:
        for row in self._rows:
            yield from row.cells

    @property
    def num_cells(self):
        return max(row.num_cells for row in self._rows)

    @property
    def num_subrows(self) -> int:
        return len(self._rows)

    @property
    def subrows(self) -> Iterable[ContentRow]:
        return iter(self._rows)

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        raise AssertionError("cannot return inflection cells in filled row")

    def contains_wordform(self, wordform: str) -> bool:
        return any(row.contains_wordform(wordform) for row in self._rows)


class Cell:
    """
    A single cell from a paradigm.
    """

    is_label: bool = False
    is_inflection: bool = False
    is_missing: bool = False
    is_empty: bool = False
    should_suppress_output: bool = False

    @staticmethod
    def parse(text: str) -> Cell:
        if text == "":
            return EmptyCell()
        elif text == "--":
            return MissingForm()
        elif text.startswith("_ "):
            return RowLabel.parse(text)
        elif text.startswith("| "):
            return ColumnLabel.parse(text)
        elif looks_like_analysis_string(text):
            return InflectionTemplate.parse(text)
        else:
            return WordformCell.parse(text)

    def contains_wordform(self, wordform: str) -> bool:
        if not self.is_inflection:
            return False
        # Must be overridden in subclasses
        raise NotImplementedError

    def fill(self, forms: Mapping[str, Collection[str]]) -> tuple[Cell, ...]:
        """
        Returns one or more cells by filling the paradigm with the provided forms.
        """
        if not self.is_inflection:
            return (self,)
        # This should be overridden by subclasses.
        # Namely, InflectionTemplate should override this.
        raise NotImplementedError

    def add_recording(self, recording):
        pass


class WordformCell(Cell):
    """
    A cell containing a displayable wordform.

    When a ParadigmLayout is filled with forms, the ParadigmLayout.fill() is
    called, converting all its InflectionTemplate instances to WordformCell instances.

    How this differs between **static** and **dynamic** paradigms:
     - **static** paradigms contain ZERO InflectionCell instances; they will all be
        WordformCell instances.
     - **dynamic** paradigms must be filled for every unique FST lemma.
    """

    is_inflection = True

    def __init__(self, inflection: str):
        self.inflection = inflection
        self.recording = None

    def contains_wordform(self, wordform: str) -> bool:
        return self.inflection == wordform

    def add_recording(self, recording):
        self.recording = recording

    def fill(self, forms: Mapping[str, Collection[str]]) -> tuple[Cell, ...]:
        # No need to fill a cell that already has contents!
        return (self,)

    def __str__(self) -> str:
        return self.inflection

    def __eq__(self, other) -> bool:
        if isinstance(other, WordformCell):
            return self.inflection == other.inflection
        return False

    def __repr__(self):
        name = type(self).__qualname__
        return f"{name}({self.inflection!r})"

    @classmethod
    def parse(cls, text: str):
        assert not looks_like_analysis_string(text)
        return cls(text)


class InflectionTemplate(Cell):
    """
    A cell that contains an inflection.
    """

    is_inflection = True

    def __init__(self, analysis: str):
        assert looks_like_analysis_string(analysis)
        self._analysis_template = string.Template(analysis)

    @property
    def analysis_template(self) -> str:
        """
        The original analysis string provided as a template for inflection,
        e.g., ${lemma}+N+Sg
        """
        return self._analysis_template.template

    def __eq__(self, other) -> bool:
        if isinstance(other, InflectionTemplate):
            return self.analysis_template == other.analysis_template
        return False

    def __str__(self):
        return self.analysis_template

    @staticmethod
    def parse(text: str) -> InflectionTemplate:
        if not looks_like_analysis_string(text):
            raise ParseError(f"cell does not look like an inflection: {text!r}")
        return InflectionTemplate(text)

    def as_analysis(self, lemma: str) -> str:
        """
        Returns a the analysis template with the substitute replaced
        """
        return self._analysis_template.substitute(lemma=lemma)

    def fill(
        self, forms: Mapping[str, Collection[str]]
    ) -> tuple[WordformCell | MissingForm, ...]:
        """
        Return one or more cells with the forms given.
        :raises ParadigmGenerationError: when the analysis is missing from the given
            forms mapping.
        """

        try:
            cell_forms = forms[self.analysis_template]
        except KeyError:
            raise ParadigmGenerationError(
                "no form(s) provided for " f"analysis: {self.analysis_template}"
            )

        if len(cell_forms) == 0:
            # It's a missing form (accidental gap/lacuna).
            # See: https://en.wikipedia.org/wiki/Accidental_gap#Morphological_gaps
            return (MissingForm(),)

        return tuple(WordformCell(form) for form in cell_forms)


class SingletonMixin:
    """
    Mixin that makes any subclasses a singleton.
    """

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        name = type(self).__qualname__
        return f"{name}()"


class MissingForm(Cell, SingletonMixin):
    """
    A missing form from the paradigm that should show up in the paradigm as a
    placeholder. Missing forms can either be hard-coded or the generator may simply
    not be able to generate a form for a given analysis.

    Note: a missing form is a valid position in the paradigm, however, we display that
    this form cannot exist. This is not the same as an empty cell, which is used as a
    spacer.
    """

    is_inflection = True
    is_missing = True

    def __str__(self):
        return "--"

    def contains_wordform(self, wordform: str) -> bool:
        """
        A missing form does not contain a wordform, be definition.
        """
        return False

    def fill(self, forms: Mapping[str, Collection[str]]) -> tuple[Cell, ...]:
        """
        A missing form is already "filled" -- return one entry
        """
        return (self,)


class EmptyCell(Cell, SingletonMixin):
    """
    A completely empty cell. This is used for spacing in the paradigm. There is no
    semantic content. Compare with MissingForm.
    """

    is_empty = True

    def __str__(self):
        return ""


class SuppressOutputCell(Cell, SingletonMixin):
    """
    Indicates that this should not be rendered at all in the paradigm.
    Note: even an EmptyCell is "output", in that a <tr> should be created for it in HTML.
    A SuppressOutputCell should not get even get a <tr>.
    """

    should_suppress_output = True


class BaseLabelCell(Cell):
    is_label = True
    label_for: str
    prefix: str

    def __init__(self, tags):
        self._tags = tuple(tags)

    @property
    def fst_tags(self) -> tuple[str]:
        return self._tags

    def __str__(self):
        return " ".join(f"{self.prefix} {tag}" for tag in self._tags)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self._tags == other._tags
        return False

    def __repr__(self):
        name = type(self).__qualname__
        return f"{name}({self._tags!r})"

    @classmethod
    def parse(cls, text: str):
        return cls(parse_label(text, prefix=cls.prefix))


class RowLabel(BaseLabelCell):
    """
    Labels for the cells in the current row within the pane.
    """

    label_for = "row"
    prefix = "_"

    def __init__(self, tags, row_span: int = 1):
        super().__init__(tags)
        self.row_span = row_span

    def with_row_span(self, span: int) -> RowLabel:
        """
        Create a brand new row label with its row span. This is intended so that an
        existing label can be used to span multiple rows.
        """
        return RowLabel(self.fst_tags, span)


class ColumnLabel(BaseLabelCell):
    """
    Labels for the cells in the current column within the pane.
    """

    label_for = "col"
    prefix = "|"


def parse_label(text: str, *, prefix: str) -> list[str]:
    """
    Parses labels in the common label syntax.

    >>> parse_label("| Ind", prefix="|")
    ['Ind']
    >>> parse_label("# Fut # Def", prefix="#")
    ['Fut', 'Def']
    >>> parse_label("_ 1Sg _ 3Sg _ Obv", prefix="_")
    ['1Sg', '3Sg', 'Obv']
    """
    splits = re.split(r" +", text)
    if len(splits) % 2 != 0:
        raise ParseError(f"Uneven number of space-separated segments in {text!r}")

    tags = []
    for actual_prefix, tag in pairs(splits):
        if actual_prefix != prefix:
            raise ParseError(f"Expected prefix {prefix!r} but saw {actual_prefix!r}")
        tags.append(tag)

    return tags


def looks_like_analysis_string(text: str) -> bool:
    """
    Returns true if the cell might be analysis.
    """
    return "${lemma}" in text


def pairs(seq):
    """
    Returns pairs from the given sequence.

    >>> list(pairs([1, 2, 3, 4, 5, 6]))
    [(1, 2), (3, 4), (5, 6)]
    """
    return zip(seq[::2], seq[1::2])


def n_empty_lists(n: int) -> list[list[Cell]]:
    """
    Returns the given number of distinct, empty lists.
    """
    return [[] for _ in range(n)]


def cell_if_exists_or_no_output(col: Sequence[Cell], row_num: int):
    """
    Extracts the content cell from the column if it exists, else returns an EmptyCell if
    nothing is found.
    """
    try:
        return col[row_num]
    except IndexError:
        return SuppressOutputCell()


def adjust_row_span(cell: Cell, span: int) -> Cell:
    """
    Fixes RowLabels such that they span the amount given. Only affects RowLabels.
    Other cells are returned as is.
    """
    if isinstance(cell, RowLabel):
        return cell.with_row_span(span)
    return cell
