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

import re
from collections import ChainMap
from enum import Enum
from typing import (Callable, Dict, List, Mapping, NamedTuple, Optional, Set,
                    Tuple)

from .data import Arc, StateID
from .data import Symbol as _Symbol
from .flags import (Clear, DisallowFeature, DisallowValue, FlagDiacritic,
                    Positive, RequireFeature, RequireValue, Unify)
from .symbol import (Epsilon, Grapheme, Identity, MultiCharacterSymbol, Symbol,
                     Unknown)

FLAG_PATTERN = re.compile(r'''
    ^@(?:
        [UPNRDE][.]\w+[.]\w+ |
        [RDC][.]\w+
    )@$
''', re.VERBOSE)


class FSTParseError(Exception):
    """
    Raise when something goes wrong parsing the FSTs.
    """


class SymbolTable:
    """
    Keeps track of ALL of the symbols in an FST.
    """
    def __init__(self) -> None:
        self.multichar_symbols = {}  # type: Dict[int, MultiCharacterSymbol]
        self.graphemes = {}  # type: Dict[int, Grapheme]
        self.flag_diacritics = {}  # type: Dict[int, FlagDiacritic]
        # Will contain:
        # 0 @_EPSILON_SYMBOL_@
        # 1 @_UNKNOWN_SYMBOL_@
        # 2 @_IDENTITY_SYMBOL_@
        self.specials = {}  # type: Dict[int, Symbol]

        # Lookup ALL of them simultaneously:
        self._combined = ChainMap(self.multichar_symbols, self.graphemes,
                                  self.flag_diacritics, self.specials)

        # TODO: differentiate between input alphabet and output alphabet
        #       the union of the two is sigma

    def __getitem__(self, idx: int):
        return self._combined[idx]

    def add(self, symbol_id: int, symbol: Symbol) -> None:
        """
        Add a symbol to the symbol table.
        """
        if isinstance(symbol, Grapheme):
            self.graphemes[symbol_id] = symbol
        elif isinstance(symbol, MultiCharacterSymbol):
            self.multichar_symbols[symbol_id] = symbol
        elif isinstance(symbol, FlagDiacritic):
            self.flag_diacritics[symbol_id] = symbol
        else:
            self.specials[symbol_id] = symbol


class FSTParse(NamedTuple('FSTParse', [('symbols', SymbolTable),
                                       ('arcs', Set[Arc]),
                                       ('intermediate_states', Set[StateID]),
                                       ('accepting_states', Set[StateID])])):
    """
    The parsed data from an FST, in a nice neat pile.
    """

    @property
    def multichar_symbols(self) -> Dict[int, MultiCharacterSymbol]:
        return self.symbols.multichar_symbols

    @property
    def flag_diacritics(self) -> Dict[int, FlagDiacritic]:
        return self.symbols.flag_diacritics

    @property
    def graphemes(self) -> Dict[int, Grapheme]:
        return self.symbols.graphemes

    @property
    def sigma(self) -> Dict[int, Symbol]:
        return {**self.multichar_symbols,
                **self.flag_diacritics,
                **self.graphemes}

    @property
    def states(self):
        return self.intermediate_states | self.accepting_states

    @property
    def has_epsilon(self) -> bool:
        return 0 in self.symbols.specials


class FomaParser:
    """
    Parses a FOMA file, in plain-text.
    """

    LineParser = Callable[[str], None]

    def __init__(self) -> None:
        self.arcs = []  # type: List[Arc]
        self.accepting_states = set()  # type: Set[StateID]
        self.implied_state = None  # type: Optional[int]
        self.handle_line = self.handle_header
        self.has_seen_header = False
        self.symbols = SymbolTable()

    def handle_header(self, line: str):
        # Nothing to do here... yet.
        ...

    def handle_props(self, line: str):
        """
        """
        if self.has_seen_header:
            raise FSTParseError('Cannot handle multiple FSTs')
        self.has_seen_header = True

        # TODO: parse:
        #  - arity
        #  - arc_count
        #  - state_count
        #  - line_count
        #  - final_count
        #  - path_count
        #  - is_deterministic
        #  - is_pruned
        #  - is_minimized
        #  - is_epsilon_free
        #  - is_loop_free
        #  - is_completed
        #  - name

        # Foma will technically accept anything until it sees '##sigma##'
        # but we won't, as that is gross.

    def handle_sigma(self, line: str):
        """
        Adds a new entry to the symbol table.
        """
        idx_str, _space, symbol_text = line.partition('\N{SPACE}')
        idx = int(idx_str)
        self.symbols.add(idx, parse_symbol(symbol_text))

    def handle_states(self, line: str):
        """
        Either:
          - appends an arc to the list;
          - adds an accepting state; or
          - finds the sentinel value
        """

        arc_def = tuple(int(num) for num in line.split())
        num_items = len(arc_def)

        if arc_def == (-1, -1, -1, -1, -1):
            # Sentinel value: there are no more arcs to define.
            return

        if num_items == 2:
            if self.implied_state is None:
                raise ValueError('No implied state')
            src = self.implied_state
            # in/out, target (state num implied)
            in_label, dest = arc_def
            out_label = in_label
        elif num_items == 3:
            if self.implied_state is None:
                raise ValueError('No implied state')
            src = self.implied_state
            # in, out, target  (state num implied)
            in_label, out_label, dest = arc_def
        elif num_items == 4:
            # FIXME: there's a bug here in my interpretation of the final parameter.
            # state num, in/out, target, final state
            src, in_label, dest, _weight = arc_def
            out_label = in_label
            # FIXME: this is a STATE WITHOUT TRANSITIONS
            if in_label == -1 or dest == -1:
                # This is an accepting state
                self.accepting_states.add(StateID(src))
                return
        elif num_items == 5:
            # FIXME: last is final_state, not weight
            src, in_label, out_label, dest, _weight = arc_def

        self.implied_state = src
        # Super important! make sure the order of these arguments is
        # consistent with the definition of Arc
        arc = Arc(StateID(src), self.symbols[in_label], self.symbols[out_label], StateID(dest))
        self.arcs.append(arc)

    def handle_end(self, line: str):
        # Nothing to do here. Yet.
        ...

    def parse_line(self, line: str):
        # Find all the details here:
        # https://github.com/mhulden/foma/blob/master/foma/io.c#L623-L821
        # Check header
        if line.startswith('##'):
            header = line[2:-2]
            self.handle_line = {
                'foma-net 1.0': self.handle_header,
                'props': self.handle_props,
                'sigma': self.handle_sigma,
                'states': self.handle_states,
                'end': self.handle_end,
            }[header]
        else:
            self.handle_line(line.rstrip('\n'))

    def finalize(self) -> FSTParse:
        # After parsing, we should be in the ##end## state.
        assert self.handle_line == self.handle_end

        states = {StateID(arc.state) for arc in self.arcs}
        return FSTParse(symbols=self.symbols,
                        arcs=set(self.arcs),
                        intermediate_states=states,
                        accepting_states=self.accepting_states)

    def parse_text(self, fst_text: str) -> FSTParse:
        for line in fst_text.splitlines():
            self.parse_line(line)

        return self.finalize()


def parse_text(att_text: str) -> FSTParse:
    """
    Parse the text of a FOMA binary FST. The text is retrieved by gunzip'ing
    the file.

    FOMA text is very similar to an AT&T format FST.
    """
    return FomaParser().parse_text(att_text)


def parse_symbol(symbol: str) -> Symbol:
    if FLAG_PATTERN.match(symbol):
        return parse_flag(symbol)
    elif symbol == '@_EPSILON_SYMBOL_@':
        return Epsilon
    elif symbol == '@_UNKNOWN_SYMBOL_@':
        return Unknown
    elif symbol == '@_IDENTITY_SYMBOL_@':
        return Identity
    elif symbol.startswith('@') and symbol.endswith('@'):
        raise NotImplementedError
    elif len(symbol) > 1:
        return MultiCharacterSymbol(symbol)
    elif len(symbol) == 1:
        return Grapheme(symbol)
    raise NotImplementedError


def parse_flag(flag_diacritic: str) -> FlagDiacritic:
    assert FLAG_PATTERN.match(flag_diacritic)
    opcode, *arguments = flag_diacritic.strip('@').split('.')
    if opcode == 'U' and len(arguments) == 2:
        return Unify(*arguments)
    elif opcode == 'P' and len(arguments) == 2:
        return Positive(*arguments)
    elif opcode == 'R' and len(arguments) == 2:
        return RequireValue(*arguments)
    elif opcode == 'R' and len(arguments) == 1:
        return RequireFeature(*arguments)
    elif opcode == 'D' and len(arguments) == 1:
        return DisallowFeature(*arguments)
    elif opcode == 'D' and len(arguments) == 2:
        return DisallowValue(*arguments)
    elif opcode == 'C' and len(arguments) == 1:
        return Clear(arguments[0])
    raise ValueError('Cannot parse ' + flag_diacritic)
