from pathlib import Path

import pytest
from hfst_optimized_lookup import TransducerFile
from more_itertools import first, ilen

from morphodict.paradigm.manager import ParadigmManager


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
    inflections = ["minôsa", "minôsak", "niminôs", "minôsinâhk"]

    paradigm = paradigm_manager.dynamic_paradigm_for(lemma=lemma, word_class=word_class)
    assert paradigm is not None

    for form in inflections:
        assert paradigm.contains_wordform(form)


@pytest.fixture
def paradigm_manager(testdata_dir: Path) -> ParadigmManager:
    layout_dir = testdata_dir / "paradigm-layouts"
    assert layout_dir.is_dir()
    assert (layout_dir / "static").is_dir()
    assert (layout_dir / "dynamic").is_dir()

    fst_dir = testdata_dir / "fst"
    generator_path = fst_dir / "crk-strict-generator.hfstol"
    assert generator_path.exists()
    strict_generator = TransducerFile(generator_path)

    return ParadigmManager(layout_dir, strict_generator)
