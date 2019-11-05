#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Classes related to paradigms: both layouts and the filled paradigms.
"""

import warnings
from typing import Iterator, List, Sequence, Union, overload

Row = Union["RowWithContent", "EmptyRowType"]
Table = List[Row]


class RowWithContent(Sequence[str]):
    """
    A row in the layout that can be filled in.

    For now, it acts like a list.
    """

    def __init__(self, cells: List[str]):
        self.cells = cells

    def __repr__(self) -> str:
        return f"RowWithContent({self.cells!r})"

    # TODO: implement .fill(x: Analyses)
    # TODO: implement .title : str

    # Make it act like a list, mostly for backwards-compatibility reasons:

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, slc: slice) -> List[str]:
        ...

    def __getitem__(self, idx: Union[slice, int]) -> Union[str, List[str]]:
        return self.cells[idx]

    def __eq__(self, other) -> bool:
        if isinstance(other, list):
            warnings.warn(
                "Comparing with a list kept only for backwards compatibility reasons.",
                DeprecationWarning,
            )
            return self.cells == other
        elif isinstance(other, RowWithContent):
            return self.cells == other.cells
        else:
            return False

    def __iter__(self) -> Iterator[str]:
        return iter(self.cells)

    def __len__(self) -> int:
        return len(self.cells)


class EmptyRowType:
    """
    A completely empty row!
    """

    def __repr__(self) -> str:
        "EmptyRow"


EmptyRow = EmptyRowType()
del EmptyRowType
