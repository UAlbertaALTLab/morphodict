"""
Integration tests for paradigms in the itwêwina (crkeng) dictionary.
"""

from pathlib import Path

import pytest
from more_itertools import first, ilen

from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.CreeDictionary.paradigm.manager import ParadigmManager


def test_generates_personal_pronoun_paradigm(paradigm_manager) -> None:
    paradigm = paradigm_manager.static_paradigm_for("personal-pronouns")
    assert paradigm is not None

    # I don't know how many panes there will be, but the first should DEFINITELY have
    # the singular personal pronouns that folks learn in basic nêhiyawêwin class.
    assert ilen(paradigm.panes) >= 1
    pane = first(paradigm.panes)
    assert pane.contains_wordform("niya")
    assert pane.contains_wordform("kiya")
    assert pane.contains_wordform("wiya")

    # The rest of the paradigm should contain the remaining pronouns
    assert paradigm.contains_wordform("niyanân")
    assert paradigm.contains_wordform("kiyânaw")
    assert paradigm.contains_wordform("kiyawâw")
    assert paradigm.contains_wordform("wiyawâw")


def test_generates_na_paradigm(paradigm_manager) -> None:
    """
    Generate a paradigm for a lemma+word class; see if it has some expected basic
    inflections.
    """
    lemma = "minôs"
    word_class = "NA"
    inflections = ["minôsa", "minôsak", "niminôs"]

    default_size = first(paradigm_manager.sizes_of(word_class))
    paradigm = paradigm_manager.paradigm_for(word_class, lemma=lemma, size=default_size)

    for form in inflections:
        assert paradigm.contains_wordform(form)


@pytest.fixture
def paradigm_manager() -> ParadigmManager:
    return default_paradigm_manager()
