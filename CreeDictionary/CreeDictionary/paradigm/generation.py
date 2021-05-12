"""
Handles paradigm generation.
"""

from functools import cache

from CreeDictionary.utils.fst_analysis_parser import extract_word_class
from CreeDictionary.utils.enums import ParadigmSize
from CreeDictionary.API.models import Wordform

from .filler import Layout, ParadigmFiller


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

    return paradigm_filler().fill_paradigm(lemma.text, word_class, size)


@cache
def paradigm_filler() -> ParadigmFiller:
    """
    Returns a cached instance of the default paradigm filler.
    """
    return ParadigmFiller.default_filler()
