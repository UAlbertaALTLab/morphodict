import unicodedata

VOWELS = {"a", "e", "i", "o"}


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


def del_dist(string, i):
    """
    custom distance for deleting a character at index i from string.
    The string is guaranteed non-empty and i is not out of bound
    """
    if i > 0 and remove_cree_diacritics(string[i - 1]) in VOWELS and string[i] == "h":
        return 0.5
    return 1


def sub_dist(string, new_char, i):
    """
    custom distance for substituting a character at index i for a new character.
    Note the string is guaranteed non-empty and i is not out-of-bound
    """
    if new_char == string[i]:
        return 0
    elif remove_cree_diacritics(string[i]) == remove_cree_diacritics(new_char):
        if remove_cree_diacritics(new_char) == "e":
            return 0
        else:
            return 0.5
    else:
        return 1


def ins_dist(string, char, i):
    """
    custom distance for inserting a character at index i to a non-empty string
    Note the string is guaranteed non-empty and  0 <= i <= len(string)
    """
    if (
        remove_cree_diacritics(string[min(i, len(string)) - 1]) in VOWELS
        and char == "h"
    ):
        return 0.5
    else:
        return 1


def get_modified_distance(spelling: str, normal_form: str) -> float:
    """
    Compute our own metric of edit distance (adapted to Cree spelling)

    An addition should have a distance of 1: e.g., minôs vs. minôhs

    A deletion should have a distance of 1: e.g., acâhkos vs. acâhko.

    A substitution should have a distance of 1: e.g., ekwa vs. ikwa

    A vowel diacritics on {a i o} change incur a distance of ½

    A vowel diacritics change on "e" should be treated as distance 0

    An addition or deletion of an 'h' in a rime should incur a distance of ½

    This function neglects letter case

    :param spelling:
    :param normal_form:
    :return: Our own metric of edit distance
    """
    # see these slides for "weighted min edit distance"
    # https://web.stanford.edu/class/cs124/lec/med.pdf
    spelling = spelling.lower()
    normal_form = normal_form.lower()
    n, m = len(spelling), len(normal_form)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        d[i][0] = d[i - 1][0] + del_dist(spelling, i - 1)
    for j in range(1, m + 1):
        d[0][j] = d[0][j - 1] + ins_dist(normal_form, normal_form[j - 1], j - 1)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            _del_dist = d[i - 1][j] + del_dist(spelling, i - 1)
            _ins_dist = d[i][j - 1] + ins_dist(normal_form, normal_form[j - 1], j - 1)
            _sub_dist = d[i - 1][j - 1] + sub_dist(spelling, normal_form[j - 1], i - 1)
            d[i][j] = min((_del_dist, _ins_dist, _sub_dist))

    return d[-1][-1]
