from enum import Enum
from typing import List, Tuple, Optional, NamedTuple

from attr import attrs
from Levenshtein import editops
import unicodedata

VOWELS = {"a", "e", "i", "o"}
CIRCUMFLEX_VOWELS = {"â", "ê", "î", "ô"}
MACRON_VOWELS = {"ā", "ē", "ī", "ō"}


def remove_cree_diacritics(input_str) -> str:
    """    
    >>> remove_cree_diacritics('ā')
    'a'
    >>> remove_cree_diacritics('â')
    'a'
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
    return only_ascii


class EditOp(NamedTuple):
    op_name: str
    source_index: int
    """The original index of the character in the original string"""
    target_index: int
    """the index of the character in the target string"""

    @staticmethod
    def apply_ops(ops: List["EditOp"], s: str, t: str) -> str:
        """This function exists to show how to interpret of EditOps obtained from `Levenshtein.editops()`"""
        s_list = list(s)
        insertion_buffers = ["" for _ in range(len(s) + 1)]

        for op_name, s_i, t_i in ops:
            if op_name == "insert":
                insertion_buffers[s_i] += t[t_i]
            elif op_name == "replace":
                s_list[s_i] = t[t_i]
            else:  # delete
                s_list[s_i] = ""

        result = ""
        for a, b in zip([""] + s_list, insertion_buffers):
            result += a + b

        return result


def get_modified_distance(spelling: str, normal_form: str) -> float:
    """
    Compute our own metric of edit distance (adapted to Cree spelling)

    An addition should have a distance of 1: e.g., minôs vs. minôhs

    A deletion should have a distance of 1: e.g., acâhkos vs. acâhko.

    A substitution should have a distance of 1: e.g., ekwa vs. ikwa

    A vowel lengths change incur a distance of ½

    An addition or deletion of an 'h' in a rime should incur a distance of ½

    This function neglects letter case

    :param spelling:
    :param normal_form:
    :return: Our own metric of edit distance
    """
    spelling = spelling.lower()
    normal_form = normal_form.lower()

    ops: List[EditOp] = editops(spelling, normal_form)
    dist = 0.0

    spelling_list = list(spelling)
    insertion_buffers = ["" for _ in range(len(spelling) + 1)]

    for op_name, s_i, t_i in ops:
        if op_name == "insert":
            insertion_buffers[s_i] += normal_form[t_i]
        elif op_name == "replace":
            spelling_list[s_i] = normal_form[t_i]
        else:  # delete
            spelling_list[s_i] = ""

    ops_and_new_indexes: List[
        Tuple[str, int]
    ] = []  # new indexes and what happened to original characters

    result = ""
    new_index_counter = 0
    for i, (mutated_char, insertions) in enumerate(
        zip([""] + spelling_list, insertion_buffers)
    ):
        if i > 0:
            original_char = spelling[i - 1]
            if mutated_char != "":
                if mutated_char == original_char:
                    ops_and_new_indexes.append(("equal", new_index_counter))
                else:
                    ops_and_new_indexes.append(("replace", new_index_counter))
            else:
                # a deletion happened
                ops_and_new_indexes.append(("delete", new_index_counter))

        if result != "":
            last_char = result[-1]
        else:
            last_char = ""

        result += mutated_char + insertions

        for x, new_char in enumerate(insertions):
            if x == 0:
                if mutated_char != "":
                    last_char = mutated_char
            else:
                last_char = insertions[x - 1]

            if last_char != "":
                # h in a rime is inserted
                if remove_cree_diacritics(last_char) in VOWELS and new_char == "h":
                    dist += 0.5
                else:
                    dist += 1
            else:
                # insertion at the beginning
                dist += 1

        new_index_counter += len(mutated_char + insertions)

    for o_index, (op_name, n_index) in enumerate(ops_and_new_indexes):
        o_char = spelling[o_index]

        if op_name == "replace":
            n_char = normal_form[n_index]
            if remove_cree_diacritics(n_char) == remove_cree_diacritics(o_char):
                dist += 0.5
            else:
                dist += 1

        elif op_name == "delete":
            if n_index == 0:
                # deleted from the start
                dist += 1
            else:
                new_char_in_front = normal_form[n_index - 1]
                if o_char == "h":
                    if remove_cree_diacritics(new_char_in_front) in VOWELS:
                        # the h is in a rime
                        dist += 0.5
                    else:
                        dist += 1
                else:
                    dist += 1
        else:  # equal
            pass

    return dist
