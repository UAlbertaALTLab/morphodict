from enum import Enum
from typing import List, Tuple, Optional

from attr import attrs


class _EditType(Enum):
    """
    different kinds of edits you can do
    """

    ADDITION = "ADDITION"
    DELETION = "DELETION"
    SUBSTITUTION = "SUBSTITUTION"


@attrs(auto_attribs=True)
class Edit:
    edit_type: _EditType
    pos: int
    char: str

    def get_distance(self):
        pass

    def perform_edit(self, word: str) -> str:

        if self.edit_type is _EditType.ADDITION:
            return word[: self.pos] + self.char + word[self.pos :]
        elif self.edit_type is _EditType.DELETION:
            return word[: self.pos] + word[self.pos :]
        else:  # substitution
            return word[: self.pos + 1] + self.char + word[self.pos :]

    def __str__(self):
        return str((self.edit_type.name, self.pos, self.char))


def _is_one_addition_away(word_a: str, word_b: str) -> Optional[Edit]:
    """test if word_b is one addition away from word_a"""
    if len(word_b) == len(word_a) + 1:
        pos = -1

        extra_met = False
        i = 0
        while i < len(word_a):
            if extra_met:
                j = i + 1
            else:
                j = i
            a_char, b_char = word_a[i], word_b[j]

            if a_char != b_char:
                if extra_met:
                    return None
                else:
                    pos = i
                    extra_met = True
                    i -= 1

            i += 1

        return Edit(
            _EditType.ADDITION, len(word_b) - 1 if pos == -1 else pos, word_b[pos]
        )


def _is_one_edit_away(word_a: str, word_b: str) -> Optional[Edit]:
    """
    >>> print(_is_one_edit_away('', ''))
    None
    >>> print(_is_one_edit_away('a', 'abc'))
    None
    >>> print(_is_one_edit_away('abc', 'a'))
    None

    >>> print(_is_one_edit_away('', 'b'))
    ('ADDITION', 0, 'b')
    >>> print(_is_one_edit_away('', ''))
    None
    >>> print(_is_one_edit_away('a', 'ab'))
    ('ADDITION', 1, 'b')
    >>> print(_is_one_edit_away('ac', 'abc'))
    ('ADDITION', 1, 'b')
    >>> print(_is_one_edit_away('ab', 'abc'))
    ('ADDITION', 2, 'c')

    >>> print(_is_one_edit_away('b', ''))
    ('DELETION', 0, 'b')
    >>> print(_is_one_edit_away('ab', 'a'))
    ('DELETION', 1, 'b')
    >>> print(_is_one_edit_away('ab', 'b'))
    ('DELETION', 0, 'a')
    >>> print(_is_one_edit_away('abc', 'ac'))
    ('DELETION', 1, 'b')
    >>> print(_is_one_edit_away('abc', 'ab'))
    ('DELETION', 2, 'c')

    >>> print(_is_one_edit_away('b', 'a'))
    ('SUBSTITUTION', 0, 'a')
    >>> print(_is_one_edit_away('ab', 'ac'))
    ('SUBSTITUTION', 1, 'c')
    >>> print(_is_one_edit_away('ab', 'bb'))
    ('SUBSTITUTION', 0, 'b')
    >>> print(_is_one_edit_away('abc', 'axc'))
    ('SUBSTITUTION', 1, 'x')
    >>> print(_is_one_edit_away('abc', 'abx'))
    ('SUBSTITUTION', 2, 'x')


    """
    addition = _is_one_addition_away(word_a, word_b)
    if addition is not None:
        return addition

    addition = _is_one_addition_away(word_b, word_a)
    if addition is not None:
        return Edit(_EditType.DELETION, addition.pos, addition.char)

    if len(word_a) == len(word_b):
        diff_met = False
        for i, (char_a, char_b) in enumerate(zip(word_a, word_b)):
            if char_a != char_b:
                if diff_met:
                    break
                else:
                    return Edit(_EditType.SUBSTITUTION, i, char_b)


def _get_shortest_edits(wordform_a: str, wordform_b: str) -> List[Edit]:
    """
    """
    if wordform_a == wordform_b:
        return []


def get_distance(wordform_a: str, wordform_b: str) -> float:
    """
    Compute our own metric of edit distance (adapted to Cree spelling)

    An addition should have a distance of 1: e.g., minôs vs. minôhs

    A deletion should have a distance of 1: e.g., acâhkos vs. acâhko.

    A substitution should have a distance of 1: e.g., ekwa vs. ikwa

    vowel lengths should incur a distance of ½

    an 'h' in a rime should incur a distance of ½

    :param wordform_a:
    :param wordform_b:
    :return: Our own metric of edit distance
    """
    shortest_edits = _get_shortest_edits(wordform_a, wordform_b)
