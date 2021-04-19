"""
Handles paradigm generation.
"""

import shared.expensive
from paradigm import Layout
from utils.fst_analysis_parser import extract_word_class
from utils.enums import ParadigmSize
from API.models import Wordform


def generate_paradigm(lemma: Wordform, size: ParadigmSize) -> list[Layout]:
    """
    :param lemma: the lemma of the desired paradigm
    :param size: the level of detail for the paradigm.
    :return: A list of filled paradigm tables.
    """
    # TODO: is there a better way to determine if this lemma inflects?
    word_class = extract_word_class(lemma.analysis)

    if word_class is None:
        # Cannot determine how the the lemma inflects; no paradigm :/
        return []

    return shared.expensive.paradigm_filler.fill_paradigm(lemma.text, word_class, size)
