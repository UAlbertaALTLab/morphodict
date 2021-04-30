"""
Provides all classes for pane-based paradigms.
"""

from __future__ import annotations

import logging
import re
import string
from functools import cached_property
from itertools import zip_longest
from typing import Collection, Iterable, Optional, TextIO

from more_itertools import first

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """
    Raised when there's an issue in parsing paradigm layouts.
    """


class ParadigmGenerationError(Exception):
    """
    Raised when there's some issue with generating/filling a paradigm.
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


# TODO: rename to ParadigmLayout -- in order to use consistent terminology
class ParadigmTemplate(Paradigm):
    """
    Template for a particular word class. The template contains analyses with
    placeholders that can be filled at runtime to generate a displayable paradigm.
    """

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        for pane in self.panes:
            yield from pane.inflection_cells

    @cached_property
    def _fst_analysis_template(self) -> string.Template:
        """
        A string template that can be given a lemma to generate FST analysis strings
        for the ENTIRE paradigm.
        """
        lines = [inflection.analysis for inflection in self.inflection_cells]
        return string.Template("\n".join(lines))

    @classmethod
    def load(cls, layout_file: TextIO) -> ParadigmTemplate:
        """
        Load a paradigm template from a file.
        """
        return cls.loads(layout_file.read())

    @classmethod
    def loads(cls, string: str) -> ParadigmTemplate:
        """
        Load a ParadigmLayout from a string.
        """
        lines = string.splitlines(keepends=False)

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
        return ParadigmTemplate(panes)

    def dumps(self):
        """
        Export the template as a string. This string can be by .loads().
        """

        pane_text = []
        num_columns = self.max_num_columns
        for pane in self.panes:
            pane_text.append(pane.dumps(require_num_columns=num_columns))

        tabs = "\t" * (num_columns - 1)
        empty_line = f"\n{tabs}\n"

        return empty_line.join(pane_text)

    def generate_fst_analysis_string(self, lemma: str) -> str:
        """
        Given a lemma, generates a string that can be fed directly to an XFST lookup
        application.
        """
        return self._fst_analysis_template.substitute(lemma=lemma)

    def fill(self, forms: dict[str, Collection[str]]) -> Paradigm:
        """
        Given a mapping from analysis to a collection of wordforms, returns a
        paradigm with all its InflectionTemplate cells replaced with WordformCells.
        """
        panes = []
        for pane in self.panes:
            rows = []
            for row in pane.rows:
                if not row.has_content:
                    rows.append(row)
                    continue
                if not isinstance(row, ContentRow):
                    raise AssertionError("This should be a content row...")
                cells = []
                for cell in row.cells:
                    if not cell.is_inflection:
                        cells.append(cell)
                        continue
                    if not isinstance(cell, InflectionTemplate):
                        raise AssertionError(f"I don't know how to fill a {cell}")
                    cells.append(cell.fill_one(forms))
                rows.append(ContentRow(cells))
            panes.append(Pane(rows))
        return Paradigm(panes)

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


class Row:
    has_content: bool
    num_cells: int

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
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
            # If we got here from ParadigmTemplate.parse(), something terrible has gone
            # wrong.
            raise ParseError("Refusing to parse empty row")

        return ContentRow(Cell.parse(t) for t in cell_texts)


class ContentRow(Row):
    """
    A single row from a pane. Rows contain cells.
    """

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, ContentRow):
            return False
        return all(a == b for a, b in zip_longest(self.cells, other.cells))

    def __str__(self):
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
    has_content = False
    num_cells = 0

    def __init__(self, tags):
        super().__init__()
        self._tags = tuple(tags)

    @property
    def inflection_cells(self) -> Iterable[InflectionTemplate]:
        # a header, by definition, has no inflections.
        return ()

    def __eq__(self, other) -> bool:
        if isinstance(other, HeaderRow):
            return self._tags == other._tags
        return False

    def __str__(self):
        tags = "+".join(self._tags)
        return f"{self.prefix} {tags}"

    def __repr__(self):
        name = type(self).__qualname__
        cells_repr = ", ".join(repr(cell) for cell in self._tags)
        return f"{name}([{cells_repr}])"

    @staticmethod
    def parse(text: str) -> HeaderRow:
        if not text.startswith("# "):
            raise ParseError("Not a header row: {text!r}")
        _prefix, _space, tags = text.rstrip().partition(" ")
        return HeaderRow(tags.split("+"))


class Cell:
    """
    A single cell from a paradigm.
    """

    is_label: bool = False
    is_inflection: bool = False
    is_empty: bool = False

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
        else:
            return InflectionTemplate.parse(text)

    def contains_wordform(self, wordform: str) -> bool:
        if not self.is_inflection:
            return False
        # Must be overridden in subclasses
        raise NotImplementedError


class WordformCell(Cell):
    """
    A cell containing a displayable wordform.

    When a ParadigmTemplate is filled with forms, the ParadigmTemplate.fill() is
    called, converting all its InflectionTemplate instances to WordformCell instances.

    How this differs between **static** and **dynamic** paradigms:
     - **static** paradigms still have InflectionTemplate instances; however, an entire
       static paradigm can be filled once and be reused every subsequent time.
     - **dynamic** paradigms must be filled for every unique FST lemma.
    """

    is_inflection = True

    def __init__(self, inflection: str):
        self.inflection = inflection

    def contains_wordform(self, wordform: str) -> bool:
        return self.inflection == wordform

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
        raise AssertionError("A literal cell can never be parsed from a template")


class InflectionTemplate(Cell):
    """
    A cell that contains an inflection.
    """

    is_inflection = True

    def __init__(self, analysis: str):
        self.analysis = analysis
        assert looks_like_analysis_string(analysis)

    def __eq__(self, other) -> bool:
        if isinstance(other, InflectionTemplate):
            return self.analysis == other.analysis
        return False

    def __str__(self):
        return self.analysis

    @staticmethod
    def parse(text: str) -> InflectionTemplate:
        if not looks_like_analysis_string(text):
            raise ParseError(f"cell does not look like an inflection: {text!r}")
        return InflectionTemplate(text)

    def fill_one(self, forms: dict[str, Collection[str]]) -> WordformCell:
        """
        Return a single WordformCell, given the fillable forms.
        """

        cell_forms = forms.get(self.analysis)
        if cell_forms is None:
            raise ParadigmGenerationError(
                "no form(s) provided for " f"analysis: {self.analysis}"
            )

        assert len(cell_forms) >= 1
        if len(cell_forms) > 1:
            logger.warning("Don't know how to output multiple forms... yet")
        form = first(sorted(cell_forms))
        return WordformCell(form)


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
    A missing form from the paradigm that should show up in the template as a placeholder.
    Note: a missing form is a valid position in the paradigm, however, we display that
    this form cannot exist. This is not the same as an empty cell, which is used as a
    spacer.
    """

    is_inflection = True

    def __str__(self):
        return "--"


class EmptyCell(Cell, SingletonMixin):
    """
    A completely empty cell. This is used for spacing in the paradigm. There is no
    semantic content. Compare with MissingForm.
    """

    is_empty = True

    def __str__(self):
        return ""


class BaseLabelCell(Cell):
    is_label = True
    label_for: str
    prefix: str

    def __init__(self, tags):
        self._tags = tuple(tags)

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
        splits = re.split(r" +", text)
        if len(splits) % 2 != 0:
            raise ParseError(f"Uneven number of space-separated segments in {text!r}")
        tags = []

        for prefix, tag in pairs(splits):
            if prefix != cls.prefix:
                raise ParseError(f"Expected prefix {cls.prefix!r} but saw {prefix!r}")
            tags.append(tag)

        return cls(tags)


class RowLabel(BaseLabelCell):
    """
    Labels for the cells in the current row within the pane.
    """

    label_for = "row"
    prefix = "_"


class ColumnLabel(BaseLabelCell):
    """
    Labels for the cells in the current column within the pane.
    """

    label_for = "column"
    prefix = "|"


def looks_like_analysis_string(text: str) -> bool:
    """
    Returns true if the cell might be analysis.
    """
    return "${lemma}" in text or "+" in text


def pairs(seq):
    """
    Returns pairs from the given sequence.

    >>> list(pairs([1, 2, 3, 4, 5, 6]))
    [(1, 2), (3, 4), (5, 6)]
    """
    return zip(seq[::2], seq[1::2])
