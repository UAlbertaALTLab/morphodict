#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Classes related to paradigms: both layouts and the filled paradigms.
"""

from typing import List, Union

RowWithContent = List[str]
Row = Union[RowWithContent, "EmptyRowType"]
Table = List[Row]


class EmptyRowType:
    """
    A completely empty row!
    """

    def __repr__(self) -> str:
        "EmptyRow"


EmptyRow = EmptyRowType()
del EmptyRowType
