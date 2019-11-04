#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Dataclasses for paradigms.
"""

from typing import Iterable, List

Row = List[str]
Table = List[Row]


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
