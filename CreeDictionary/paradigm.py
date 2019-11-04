#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Dataclasses for paradigms.
"""

from typing import Any, Iterable, List, Sized


class Pane(Iterable[Row]):
    """
    A section of a larger paradigm.

    A pane contains one or more rows.
    """

    def __init__(self, rows: List[Row] = None):
        if rows is not None:
            self._rows = rows.copy()
        else:
            self._rows = []

    def __iter__(self):
        return iter(self._rows)

    def __repr__(self) -> str:
        return f"Pane(rows={self._rows})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Pane):
            return False

        return self._rows == other._rows


class Row:
    is_empty_row: bool = False


class EmptyRow(Row):
    is_empty_row = True


class ContentRow(Row, Iterable[str], Sized):
    def __init__(self, columns: List[str]):
        self._cols = columns.copy()

    def __iter__(self):
        return iter(self._cols)

    def __len___(self):
        return len(self._cols)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ContentRow):
            return False

        return self._cols == other._cols


Layout = List[Row]
