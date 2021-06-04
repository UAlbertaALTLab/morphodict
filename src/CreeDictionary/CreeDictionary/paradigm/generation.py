"""
Handles paradigm generation.
"""

from functools import cache

from CreeDictionary.API.models import Wordform
from CreeDictionary.CreeDictionary.paradigm.filler import Layout, ParadigmFiller
from CreeDictionary.shared import expensive
from CreeDictionary.utils import shared_res_dir
from CreeDictionary.utils.enums import ParadigmSize
from CreeDictionary.utils.fst_analysis_parser import extract_word_class
from morphodict.paradigm.manager import ParadigmManager


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


@cache
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts and FST from the res
    (resource) directory.
    """
    return ParadigmManager(shared_res_dir / "layouts", expensive.strict_generator)
