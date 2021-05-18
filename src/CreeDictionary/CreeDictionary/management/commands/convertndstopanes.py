"""
Converts all loaded paradigm templates and outputs them in the pane-style template.

Note: this code is **temporary**! (2021-04-23)
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Protocol, Sequence

from django.core.management import BaseCommand
from CreeDictionary.utils import ParadigmSize

from CreeDictionary.CreeDictionary.paradigm.filler import EmptyRow, TitleRow
from CreeDictionary.CreeDictionary.paradigm.generation import paradigm_filler
from CreeDictionary.CreeDictionary.paradigm.panes import (
    Cell,
    ColumnLabel,
    ContentRow,
    EmptyCell,
    HeaderRow,
    InflectionTemplate,
    MissingForm,
    Pane,
    ParadigmLayout,
    RowLabel,
)
from CreeDictionary.CreeDictionary.relabelling import LABELS


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("outdir", help="where to save the new panes", type=Path)
        parser.add_argument(
            "-f", "--force", help="overwrites files if present", action="store_true"
        )

    def handle(self, *, outdir: Path, force=False, **options):
        existing_paradigms = paradigm_filler()
        english_templates = snoop_all_plain_english_templates(existing_paradigms)
        self.label_to_tags = snoop_unambiguous_plain_english_tags()

        outdir.mkdir(exist_ok=True)

        for word_class, full_paradigm in english_templates.items():
            pane_file = outdir / f"{word_class.value}.tsv"

            if pane_file.exists() and not force:
                print("not overwriting", pane_file)
                continue

            paradigm_template = self.convert_layout_to_new_format(full_paradigm)
            pane_file.write_text(paradigm_template.dumps(), encoding="UTF-8")

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
                if tags := self.label_to_tags.get(row.title):
                    rows.append(HeaderRow(tags))
                else:
                    rows.append(UnknownHeaderRow(row.title))
                continue

            cells = []
            first_cell = True
            for cell in row:
                new_cell: Cell
                if cell == "":
                    new_cell = EmptyCell()
                elif hasattr(cell, "analysis"):
                    if analysis := cell.analysis:
                        new_cell = InflectionTemplate(analysis.template)
                    else:
                        new_cell = MissingForm()
                elif cell.is_label or hasattr(cell, "text"):
                    new_cell = self.cell_template_from_text(cell.text, first_cell)
                else:
                    raise AssertionError("Not sure what type this is")
                cells.append(new_cell)
                first_cell = False

            rows.append(ContentRow(cells))

        return ParadigmLayout(Pane(rows) for rows in panes)


class _ExpectedMixinBase(Protocol):
    """
    UnknownLabelTagMixin should be mixed into a class that looks like this:
    """

    prefix: str

    def __init__(self, t: Sequence[str]) -> None:
        ...


class UnknownLabelTagMixin(_ExpectedMixinBase):
    """
    Mixin to a Label or a Header to display <!ORIGINAL LABEL!> instead of an FST tag.
    """

    UNANALYZABLE = ("?",)

    def __init__(self, original: str):
        super().__init__(self.UNANALYZABLE)
        self.original = original

    def __str__(self):
        return f"{self.prefix} <!{self.original}!>"


class UnknownHeaderRow(UnknownLabelTagMixin, HeaderRow):
    """
    A header row whose tag cannot be looked up.
    """


class UnknownRowLabel(UnknownLabelTagMixin, RowLabel):
    """
    A row with a label that cannot be looked up
    """


class UnknownColumnLabel(UnknownLabelTagMixin, ColumnLabel):
    """
    A column with a label that cannot be looked up
    """


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
