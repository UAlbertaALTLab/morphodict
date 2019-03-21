#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2019 Eddie Antonio Santos <easantos@ualberta.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC, abstractmethod


class Symbol(ABC):
    """
    A symbol in the FST.
    """

    # Note: these class variables are not strictly-necessary, but checking
    # them are a bit quicker than isinstance() check:

    # Subclasses should override this to indicate if their str() is usable a
    # graphical symbol.
    is_graphical_symbol = False
    # Subclasses should override them if this symbol should be treated like a
    # flag diacritic.
    is_flag_diacritic = False


class EpsilonType(Symbol):
    def __repr__(self) -> str:  # pragma: no cover
        return 'Epsilon'

    def __str__(self) -> str:  # pragma: no cover
        # Print an epsilon in reverse video, to distinguish it from a literal epsilon.
        return '\033[7m' 'ε' '\033[27m'


class UnknownType(Symbol):
    pass


class IdentityType(Symbol):
    pass


Unknown = UnknownType()
Identity = IdentityType()
Epsilon = EpsilonType()


class GraphicalSymbol(Symbol):
    """
    Base class for graphical symbols: Grapheme and MultiCharacterSymbol.
    """
    __slots__ = '_value',

    is_graphical_symbol = True

    def __init__(self, value: str) -> None:
        self._value = value

    def __eq__(self, other) -> bool:
        # Originally there were isinstance() checks here, but they are
        # SLOOOW!  Instead, we're doing this technically unsafe lookup, hoping
        # that IF the other object has a ._value attribute, it's a graphical
        # symbol, and this comparison is valid. It may not be in all cases :/
        try:
            # not (a != b) coerces the answer to bool, without costly call to bool()
            return not (other._value != self._value)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash((type(self).__qualname__, self._value))

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:  # pragma: no cover
        return '{:}({!r})'.format(type(self).__name__, self._value)


class Grapheme(GraphicalSymbol):
    """
    Represents a single graphical character.
    """

    def __init__(self, char: str) -> None:
        assert len(char) == 1
        super().__init__(char)


class MultiCharacterSymbol(GraphicalSymbol):
    """
    Usually represents a tag or a feature.
    """

    def __init__(self, tag: str) -> None:
        assert len(tag) > 1
        super().__init__(tag)
