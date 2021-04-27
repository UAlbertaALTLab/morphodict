from __future__ import annotations

"""
Provides all classes for pane-based paradigms.
"""

import re
from itertools import zip_longest
from typing import Iterable, Optional, TextIO


class ParseError(Exception):
    """
    Raised when there's an issue in parsing paradigm layouts.
    """


class ParadigmTemplate:
    """
    Template for a particular word class. The template contains analyses with
    placeholders that can be filled at runtime to generate a displayable paradigm.
    """

    def __init__(self, panes: Iterable[Pane]):
        self._panes = tuple(panes)

    def panes(self):
        yield from self._panes

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
        # TODO: write property test: p == ParadigmTemplate.loads(p.dumps())
        pane_text = []
        for pane in self.panes():
            pane_text.append(str(pane))

        return "\n\n".join(pane_text)

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
        return len(max(self._rows, key=len))

    def rows(self):
        yield from self._rows

    def __str__(self):
        return "\n".join(str(row) for row in self.rows())

    @classmethod
    def parse(cls, text: str) -> Pane:
        lines = text.splitlines()

        if len(lines) == 0:
            raise ParseError("Not enough lines in pane")

        return Pane(Row.parse(line) for line in lines)


class Row:
    """
    A single row from a pane. Rows contain cells.
    """

    def __init__(self, cells: Iterable[Cell]):
        self._cells = tuple(cells)

    def cells(self):
        yield from self._cells

    def __eq__(self, other) -> bool:
        if not isinstance(other, Row):
            return False
        return all(a == b for a, b in zip_longest(self.cells(), other.cells()))

    def __str__(self):
        return "\t".join(str(cell) for cell in self.cells())

    def __repr__(self):
        name = type(self).__qualname__
        cells_repr = ", ".join(repr(cell) for cell in self.cells())
        return f"{name}([{cells_repr}])"

    def __len__(self):
        return len(self._cells)

    @staticmethod
    def parse(text: str) -> Row:
        if text.startswith("# "):
            return HeaderRow.parse(text)
        cell_texts = text.rstrip("\n").split("\t")

        while cell_texts:
            if cell_texts[-1].strip() != "":
                break
            cell_texts.pop()

        return Row(Cell.parse(t) for t in cell_texts)


class HeaderRow(Row):
    """
    A row that acts as a header for the rest of the pane.
    """

    def __init__(self, tags_or_header):
        super().__init__(())

        # TODO: this should only handle tags!
        # TODO: drop support for _original_title
        if isinstance(tags_or_header, str):
            self._original_title = tags_or_header
        else:
            self._tags = tuple(tags_or_header)

    def __len__(self) -> int:
        """
        Headers always have exactly one cell.
        """
        return 1

    def __str__(self):
        if hasattr(self, "_tags"):
            tags = "+".join(self._tags)
            return f"# {tags}"
        else:
            return f"# <!{self._original_title}!>"

    @staticmethod
    def parse(text: str) -> HeaderRow:
        if not text.startswith("# "):
            raise ParseError("Not a header row: {text!r}")
        _prefix, _space, tags = text.partition(" ")
        return HeaderRow(tags.split("+"))


class Cell:
    """
    A single cell from a paradigm.
    """

    is_label: bool = False
    is_inflection: bool = False
    is_empty = bool = False

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
            return InflectionCell.parse(text)


class InflectionCell(Cell):
    """
    A cell that contains an inflection.
    """

    is_inflection = True

    def __init__(self, analysis: str):
        self.analysis = analysis
        assert "${lemma}" in analysis or "+" in analysis

    def __eq__(self, other) -> bool:
        if isinstance(other, InflectionCell):
            return self.analysis == other.analysis
        return False

    def __str__(self):
        return self.analysis

    @staticmethod
    def parse(text: str) -> InflectionCell:
        if "${lemma}" not in text and "+" not in text:
            raise ParseError(f"cell does not look like an inflection: {text!r}")
        return InflectionCell(text)


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
            raise ParseError(f"Uneven number of space separated segments in {text!r}")
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


def pairs(seq):
    """
    Returns pairs from the given sequence.

    >>> list(pairs([1, 2, 3, 4, 5, 6]))
    [(1, 2), (3, 4), (5, 6)]
    """
    return zip(seq[::2], seq[1::2])
