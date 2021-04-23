from __future__ import annotations

"""
Converts all loaded paradigm templates and outputs them in the pane-style template.

Note: this code is **temporary**! (2021-04-23)
"""

import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

from django.core.management import BaseCommand
from utils import ParadigmSize, WordClass, shared_res_dir  # type: ignore

from CreeDictionary.paradigm.filler import EmptyRow, TitleRow  # type: ignore
from CreeDictionary.paradigm.generation import paradigm_filler  # type: ignore
from CreeDictionary.relabelling import LABELS, _LabelFriendliness  # type: ignore


class ErrorOnStr(str):
    def __str__(self):
        raise TypeError("Cannot render string")


def identity(x):
    return x


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
del EmptyCellType


class BaseLabelCell(CellTemplate):
    is_label = True
    label_for: str = ErrorOnStr()
    prefix: str = ErrorOnStr()


class LabelFromTagMixin(BaseLabelCell):
    def __init__(self, tags):
        self._tags = tags

    def __str__(self):
        return " ".join(f"{self.prefix} {tag}" for tag in self._tags)


class UnknownLabelTagMixin(BaseLabelCell):
    def __init__(self, original: str):
        self.original = original

    def __str__(self):
        return f"{self.prefix} <!{self.original}!>"


class BaseRowLabel(BaseLabelCell):
    label_for = "row"
    prefix = "_"


class BaseColumnLabel(BaseLabelCell):
    label_for = "column"
    prefix = "|"


class RowLabel(BaseRowLabel, LabelFromTagMixin):
    ...


class ColumnLabel(BaseColumnLabel, LabelFromTagMixin):
    ...


class UnknownRowLabel(BaseRowLabel, UnknownLabelTagMixin):
    ...


class UnknownColumnLabel(BaseColumnLabel, UnknownLabelTagMixin):
    ...


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
            return f"= {tags}"
        else:
            return f"= <!{self._original_title}!>"


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


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "outdir",
            nargs="?",
            help="where to save the new panes",
        )

    def handle(self, *args, **options):
        existing_paradigms = paradigm_filler()
        english_templates = snoop_all_plain_english_templates(existing_paradigms)
        self.label_to_tags = snoop_unambiguous_plain_english_tags()

        for word_class, full_paradigm in english_templates.items():
            paradigm_template = self.convert_layout_to_new_format(full_paradigm)
            print("=====", word_class, "======")
            print(paradigm_template)
            print()

    def cell_template_from_text(self, text, is_first_cell):
        if tags := self.label_to_tags.get(text):
            if is_first_cell:
                return RowLabel(tags)
            else:
                return ColumnLabel(tags)
        else:
            if is_first_cell:
                return UnknownRowLabel(text)
            else:
                return UnknownColumnLabel(text)

    def convert_layout_to_new_format(self, layout):
        panes = [[]]

        # This is the old paradigm "layout" data structure:
        # layout: list[Row]
        # Row: list[Cell] | EmptyRow | TitleRow
        # Cell: Label | InflectionCell
        for row in layout:
            if row is EmptyRow:
                # start a new pane
                panes.append([])
                continue

            rows = panes[-1]

            if isinstance(row, TitleRow):
                tags = self.label_to_tags.get(row.title)
                rows.append(HeaderRow(tags or row.title))
                continue

            cells = []
            first_cell = True
            for cell in row:
                new_cell: CellTemplate
                if cell == "":
                    new_cell = EmptyCell
                elif hasattr(cell, "analysis"):
                    if analysis := cell.analysis:
                        new_cell = InflectionCellTemplate(analysis.template)
                    else:
                        new_cell = MissingForm()
                elif cell.is_label:
                    new_cell = self.cell_template_from_text(cell.text, first_cell)
                cells.append(new_cell)
                first_cell = False

            rows.append(RowTemplate(cells))

        return ParadigmTemplate(Pane(rows) for rows in panes)


def snoop_unambiguous_plain_english_tags():
    """
    Peer into relabelling to convert linguistic labels back to tags.
    """

    from CreeDictionary.relabelling import _LabelFriendliness  # type: ignore

    label_to_tags = defaultdict(list)
    for tag, relabellings in LABELS._data.items():
        label = relabellings.get(_LabelFriendliness.ENGLISH)
        if label is None:
            lazy_log("No English label for", tag)
            continue
        label_to_tags[label].append(tag)

    label_to_unambiguous_tag = {}
    for label, tags in label_to_tags.items():
        if len(tags) == 1:
            label_to_unambiguous_tag[label] = tags[0]
        else:
            lazy_log("Ambiguous label:", label)
            lazy_log("   => maps to", tags)

    return label_to_unambiguous_tag


def snoop_all_plain_english_templates(filler):
    """
    Peers into ParadigmFiller's private internal data structures to recover ONLY the
    plain English paradigms.
    """
    desired_layouts = {}
    for (wordclass, category), layout in filler._layout_tables.items():
        if category is not ParadigmSize.FULL:
            continue
        desired_layouts[wordclass] = layout

    return desired_layouts


def lazy_log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
