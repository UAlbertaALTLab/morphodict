"""
This module hides some gross code behind using an optional search key.

In my opinion, this module demonstrates where the current static-typing system in
Python is at its worst, and dynamic typing shines.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar

# Required to annotate functions that take a T and return a T.
_T = TypeVar("_T")

# Here are some protocols inspired by **unstable** protocols defined in the
# semi-secret, type-checking only _typeshed module:
# See: https://github.com/python/typeshed/blob/0d9521970d3794b521d798fddfd974de2fd0a534/stdlib/_typeshed/__init__.pyi#L25-L28


class _SupportsLessThan(Protocol):
    """
    Represents a type that can be compared with less-than against ANYTHING else.

    Note: You probably want the bounded version (SupportsLessThan), so that Any can be
    substituted with a more narrow type.
    """

    def __lt__(self, _other: Any) -> bool:
        ...


SupportsLessThan = TypeVar("SupportsLessThan", bound=_SupportsLessThan)

# Based on: https://github.com/python/typeshed/blob/0d9521970d3794b521d798fddfd974de2fd0a534/stdlib/builtins.pyi#L1294
# A key function
KeyFunction = Callable[[_T], SupportsLessThan]


def position_in_list(reference: list[str]) -> KeyFunction:
    """
    Returns a key function that will sort an element by its position in the given list.
    """
    map_element_to_index = {element: index for index, element in enumerate(reference)}

    def key_function(element: str):
        return map_element_to_index[element]

    return key_function
