from __future__ import annotations


class CellTemplate:
    is_label: bool = False
    is_inflection: bool = False
    is_empty = bool = False


class InflectionCellTemplate(CellTemplate):
    is_inflection = True

    def __init__(self, analysis: str):
        self.analysis = analysis
        assert "{{lemma}}" in analysis or "+" in analysis

    def __str__(self):
        return self.analysis


class MissingForm(InflectionCellTemplate):
    def __init__(self):
        pass

    def __str__(self):
        return "--"


class EmptyCellType(CellTemplate):
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


class BaseLabelCell(CellTemplate):
    is_label = True
    label_for: str
    prefix: str

    def __init__(self, tags):
        self._tags = tags

    def __str__(self):
        return " ".join(f"{self.prefix} {tag}" for tag in self._tags)


class RowLabel(BaseLabelCell):
    label_for = "row"
    prefix = "_"


class ColumnLabel(BaseLabelCell):
    label_for = "column"
    prefix = "|"


class RowTemplate:
    def __init__(self, cells: list[CellTemplate]):
        self._cells = tuple(cells)

    def cells(self):
        yield from self._cells

    def __str__(self):
        return "\t".join(str(cell) for cell in self.cells())


class HeaderRow(RowTemplate):
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


class Pane:
    def __init__(self, rows: list[RowTemplate]):
        self._rows = tuple(rows)

    def rows(self):
        yield from self._rows

    def __str__(self):
        return "\n".join(str(row) for row in self.rows())


class ParadigmTemplate:
    def __init__(self, panes: list[Pane]):
        self._panes = tuple(panes)

    def panes(self):
        yield from self._panes

    @classmethod
    def loads(cls, string):
        raise NotImplementedError

    def dumps(self):
        pane_text = []
        for pane in self.panes():
            pane_text.append(str(pane))

        return "\n\n".join(pane_text)

    def __str__(self):
        return self.dumps()
