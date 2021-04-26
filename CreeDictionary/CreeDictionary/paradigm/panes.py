from __future__ import annotations

"""
Provides all classes for pane-based paradigms.
"""


class ParadigmTemplate:
    """
    Template for a particular word class. The template contains analyses with
    placeholders that can be filled at runtime to generate a displayable paradigm.
    """

    def __init__(self, panes: list[Pane]):
        self._panes = tuple(panes)

    def panes(self):
        yield from self._panes

    @classmethod
    def loads(cls, string):
        raise NotImplementedError

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
    def __init__(self, rows: list[Row]):
        self._rows = tuple(rows)

    def rows(self):
        yield from self._rows

    def __str__(self):
        return "\n".join(str(row) for row in self.rows())


class Row:
    """
    A single row from a pane. Rows contain cells.
    """

    def __init__(self, cells: list[Cell]):
        self._cells = tuple(cells)

    def cells(self):
        yield from self._cells

    def __str__(self):
        return "\t".join(str(cell) for cell in self.cells())


class HeaderRow(Row):
    """
    A row that acts as a header for the rest of the pane.
    """

    def __init__(self, tags_or_header):
        if isinstance(tags_or_header, tuple):
            self._tags = tags_or_header
        else:
            assert isinstance(tags_or_header, str)
            self._original_title = tags_or_header

    def __str__(self):
        if hasattr(self, "_tags"):
            tags = "+".join(self._tags)
            return f"# {tags}"
        else:
            return f"# <!{self._original_title}!>"


class Cell:
    """
    A single cell from a paradigm.
    """
    is_label: bool = False
    is_inflection: bool = False
    is_empty = bool = False


class InflectionCell(Cell):
    """
    A cell that contains an inflection.
    """
    is_inflection = True

    def __init__(self, analysis: str):
        self.analysis = analysis
        assert "{{lemma}}" in analysis or "+" in analysis

    def __str__(self):
        return self.analysis


class MissingForm(Cell):
    """
    A missing form from the paradigm that should show up in the template as a placeholder.
    Note: a missing form is a valid position in the paradigm, however, we display that
    this form cannot exist. This is not the same as an empty cell, which is used as a
    spacer.
    """
    is_inflection = True

    def __str__(self):
        return "--"


class EmptyCellType(Cell):
    """
    A completely empty cell. This is used for spacing in the paradigm. There is no
    semantic content. Compare with MissingForm.
    """
    is_empty = True

    def __new__(cls) -> EmptyCellType:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __str__(self):
        return ""

    def __repr__(self):
        return "EmptyCell"


EmptyCell = EmptyCellType()


class BaseLabelCell(Cell):
    is_label = True
    label_for: str
    prefix: str

    def __init__(self, tags):
        self._tags = tags

    def __str__(self):
        return " ".join(f"{self.prefix} {tag}" for tag in self._tags)


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
