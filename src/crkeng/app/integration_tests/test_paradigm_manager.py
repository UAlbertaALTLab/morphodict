"""
Integration tests for paradigms in the itwêwina (crkeng) dictionary.
"""

from pathlib import Path

import pytest
from more_itertools import first, ilen

from morphodict.paradigm.generation import default_paradigm_manager
from morphodict.paradigm.manager import (
    ParadigmManager,
    ParadigmManagerWithExplicitSizes,
)


def test_paradigm_sizes_are_ordered(paradigm_manager):
    assert isinstance(paradigm_manager, ParadigmManagerWithExplicitSizes)
    assert (
        paradigm_manager.all_sizes_fully_specified()
    ), "please check MORPHODICT_PARADIGM_SIZES or the names of the .tsv files"


def test_generates_personal_pronoun_paradigm(paradigm_manager) -> None:
    paradigm = paradigm_manager.paradigm_for("personal-pronouns")
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


@pytest.mark.parametrize(
    ("name", "lemma", "examples"),
    [
        ("VTA", "wâpamêw", ["wâpamêw", "niwâpamâw", "kiwâpamitin", "ê-wâpamât"]),
        ("VAI", "nipâw", ["nipâw", "ninipân", "kinipân", "ninipânân"]),
        ("VTI", "mîciw", ["mîciw", "nimîcin", "kimîcin", "kimîcinânaw", "ê-mîcit"]),
        ("VAI", "mîcisow", ["mîcisow", "nimîcison", "kimîcison", "ê-mîcisoyit"]),
        ("VII", "nîpin", ["nîpin", "nîpin", "ê-nîpihk"]),
        ("NDA", "nôhkom", ["nôhkom", "kôhkom", "ohkoma"]),
        ("NDI", "mîpit", ["mîpit", "nîpit", "kîpit", "wîpit"]),
        ("NA", "minôs", ["minôs", "minôsak", "minôsa"]),
        ("NI", "nipiy", ["nipiy", "nipîhk", "ninipîm", "kinipîm"]),
    ],
)
def test_paradigm(paradigm_manager, name, lemma, examples: list[str]):
    default_size = first(paradigm_manager.sizes_of(name))
    paradigm = paradigm_manager.paradigm_for(name, lemma=lemma, size=default_size)

    for form in examples:
        assert paradigm.contains_wordform(form)


def test_generates_na_paradigm(paradigm_manager) -> None:
    """
    Generate a paradigm for a lemma+word class; see if it has some expected basic
    inflections.
    """
    lemma = "minôs"
    word_class = "NA"
    inflections = ["minôsa", "minôsak", "niminôsim"]

    default_size = first(paradigm_manager.sizes_of(word_class))
    paradigm = paradigm_manager.paradigm_for(word_class, lemma=lemma, size=default_size)

    for form in inflections:
        assert paradigm.contains_wordform(form)


@pytest.fixture
def paradigm_manager() -> ParadigmManager:
    return default_paradigm_manager()
