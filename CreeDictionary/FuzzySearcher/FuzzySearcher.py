# https://gist.github.com/Arachnid/491973
import bisect
from typing import List, TypeVar, Optional, Iterable, Generic

from typing_extensions import Protocol


class SupportsStr(Protocol):
    """
    word object that's fed into the automaton
    """

    def __str__(self) -> str:
        """
        :return: the word
        """
        ...


class NFA:
    EPSILON = object()
    ANY = object()

    def __init__(self, start_state):
        self.transitions = {}
        self.final_states = set()
        self._start_state = start_state

    @property
    def start_state(self):
        return frozenset(self._expand({self._start_state}))

    def add_transition(self, src, input, dest):
        self.transitions.setdefault(src, {}).setdefault(input, set()).add(dest)

    def add_final_state(self, state):
        self.final_states.add(state)

    def is_final(self, states):
        return self.final_states.intersection(states)

    def _expand(self, states):
        frontier = set(states)
        while frontier:
            state = frontier.pop()
            new_states = (
                self.transitions.get(state, {})
                .get(NFA.EPSILON, set())
                .difference(states)
            )
            frontier.update(new_states)
            states.update(new_states)
        return states

    def next_state(self, states, input):
        dest_states = set()
        for state in states:
            state_transitions = self.transitions.get(state, {})
            dest_states.update(state_transitions.get(input, []))
            dest_states.update(state_transitions.get(NFA.ANY, []))
        return frozenset(self._expand(dest_states))

    def get_inputs(self, states):
        inputs = set()
        for state in states:
            inputs.update(self.transitions.get(state, {}).keys())
        return inputs

    def to_dfa(self):
        dfa = DFA(self.start_state)
        frontier = [self.start_state]
        seen = set()
        while frontier:
            current = frontier.pop()
            inputs = self.get_inputs(current)
            for input in inputs:
                if input == NFA.EPSILON:
                    continue
                new_state = self.next_state(current, input)
                if new_state not in seen:
                    frontier.append(new_state)
                    seen.add(new_state)
                    if self.is_final(new_state):
                        dfa.add_final_state(new_state)
                if input == NFA.ANY:
                    dfa.set_default_transition(current, new_state)
                else:
                    dfa.add_transition(current, input, new_state)
        return dfa


class DFA:
    def __init__(self, start_state):
        self.start_state = start_state
        self.transitions = {}
        self.defaults = {}
        self.final_states = set()

    def add_transition(self, src, input, dest):
        self.transitions.setdefault(src, {})[input] = dest

    def set_default_transition(self, src, dest):
        self.defaults[src] = dest

    def add_final_state(self, state):
        self.final_states.add(state)

    def is_final(self, state):
        return state in self.final_states

    def next_state(self, src, input):
        state_transitions = self.transitions.get(src, {})
        return state_transitions.get(input, self.defaults.get(src, None))

    def next_valid_string(self, input):
        state = self.start_state
        stack = []

        # Evaluate the DFA as far as possible
        for i, x in enumerate(input):
            stack.append((input[:i], state, x))
            state = self.next_state(state, x)
            if not state:
                break
        else:
            stack.append((input[: i + 1], state, None))

        if self.is_final(state):
            # Input word is already valid
            return input

        # Perform a 'wall following' search for the lexicographically smallest
        # accepting state.
        while stack:
            path, state, x = stack.pop()
            x = self.find_next_edge(state, x)
            if x:
                path += x
                state = self.next_state(state, x)
                if self.is_final(state):
                    return path
                stack.append((path, state, None))
        return None

    def find_next_edge(self, s, x):
        if x is None:
            x = u"\0"
        else:
            x = chr(ord(x) + 1)
        state_transitions = self.transitions.get(s, {})
        if x in state_transitions or s in self.defaults:
            return x
        labels = sorted(state_transitions.keys())
        pos = bisect.bisect_left(labels, x)
        if pos < len(labels):
            return labels[pos]
        return None


def levenshtein_automata(term: str, k):
    nfa = NFA((0, 0))
    for i, c in enumerate(term):
        for e in range(k + 1):
            # Correct character
            nfa.add_transition((i, e), c, (i + 1, e))
            if e < k:
                # Deletion
                nfa.add_transition((i, e), NFA.ANY, (i, e + 1))
                # Insertion
                nfa.add_transition((i, e), NFA.EPSILON, (i + 1, e + 1))
                # Substitution
                nfa.add_transition((i, e), NFA.ANY, (i + 1, e + 1))
    for e in range(k + 1):
        term_len = len(term)
        if e < k:
            nfa.add_transition((term_len, e), NFA.ANY, (term_len, e + 1))
        nfa.add_final_state((term_len, e))
    return nfa


T = TypeVar("T", covariant=True)


class OrderedIterableCorpus(Protocol[T]):
    """
    A corpus where T is the type of component
    """

    def get_next_smaller(self, lookup_string: str) -> Optional[SupportsStr]:
        """
        needed to perform fuzzy search
        """
        ...

    def strings_to_elements(self, results: List[str]) -> Iterable[T]:
        """
        how to convert the result strings to the
        """
        ...


WordType = TypeVar("WordType")


class FuzzySearcher(Generic[WordType]):
    def __init__(self, words: OrderedIterableCorpus[WordType]):
        """
        :param words: a list of database entries you want to include
        """
        self._words = words
        self._probes = 0

    def search(self, word_string: str, k: int) -> Iterable[WordType]:
        """Uses lookup_func to find all words within levenshtein distance k of word.

        Args:
          word_string: The word to look up
          k: Maximum edit distance
          lookup_func: A single argument function that returns the first word in the
            database that is less than or equal to the input argument.
        Yields:
          Every matching word within levenshtein distance k from the database.
        """
        lev = levenshtein_automata(word_string, k).to_dfa()
        match = lev.next_valid_string(u"\0")
        strings = []
        while match:
            next_word = self._words.get_next_smaller(match)
            if not next_word:
                break
            next_word_text = str(next_word)
            if match == str(next_word):
                strings.append(match)
                next_word_text += u"\0"
            match = lev.next_valid_string(next_word_text)
        return self._words.strings_to_elements(strings)
