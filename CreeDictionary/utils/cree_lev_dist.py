from enum import Enum


class Edit(Enum):
    """
    different kinds of edits you can do
    """

    ADDITION = "ADDITION"
    DELETION = "DELETION"
    SUBSTITUTION = "SUBSTITUTION"


def _get_distance(wordform_a: str, wordform_b: str):
    pass


def get_shortest_distance(wordform_a: str, wordform_b: str) -> float:
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
    pass
