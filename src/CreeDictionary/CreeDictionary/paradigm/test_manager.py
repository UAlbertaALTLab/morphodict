import random
import re
from pathlib import Path
from typing import Iterable

import pytest

from CreeDictionary.CreeDictionary.paradigm.manager import ONLY_SIZE, ParadigmManager, \
    Transducer
from CreeDictionary.CreeDictionary.paradigm.sort_utils import position_in_list


def test_one_size(paradigm_manager: ParadigmManager):
    assert set(paradigm_manager.sizes_of("has-only-one-size")) == {ONLY_SIZE}

    paradigm = paradigm_manager.paradigm_for(
        "has-only-one-size", lemma="everything bagel"
    )

    all_forms = [
        "everything bagel",
        "buttered everything bagel",
        "cream cheese everything bagel",
    ]

    for form in all_forms:
        assert paradigm.contains_wordform(form), f"{form} not found in {paradigm}"


def test_multiple_sizes(paradigm_manager: ParadigmManager):
    expected_sizes = {"tall", "grande", "venti"}
    assert set(paradigm_manager.sizes_of("has-multiple-sizes")) == expected_sizes


def test_sizes_are_sorted(coffee_layout_dir: Path, identity_transducer):
    paradigm_name = "has-multiple-sizes"
    expected_sizes = {"tall", "grande", "venti"}

    wacky_ordering = distinct_permutation(expected_sizes)
    manager = ParadigmManager(
        coffee_layout_dir,
        identity_transducer,
        sort_sizes_by=position_in_list(wacky_ordering)
    )

    actual_sizes = list(manager.sizes_of(paradigm_name))
    assert actual_sizes == wacky_ordering


def test_can_find_wordforms_in_multiple_sizes(paradigm_manager: ParadigmManager):
    lemma = "caramel macchiato"

    # For those not familiar with a certain Seattle-based coffee chain:
    # "tall" is the smallest size
    # "grande" is the medium size
    # "venti" is the largest size
    # Pedantic note: There's also "short" and "trenti", but let's not.
    tall = paradigm_manager.paradigm_for("has-multiple-sizes", lemma=lemma, size="tall")
    grande = paradigm_manager.paradigm_for(
        "has-multiple-sizes", lemma=lemma, size="grande"
    )
    venti = paradigm_manager.paradigm_for(
        "has-multiple-sizes", lemma=lemma, size="venti"
    )

    present_in_all_sizes = [lemma]
    exclusively_in_grande_and_up = [f"iced {lemma}"]
    exclusively_in_venti = [f"iced almond {lemma}, no whip"]

    for form in present_in_all_sizes:
        for size in (tall, grande, venti):
            assert size.contains_wordform(form)

    for form in exclusively_in_grande_and_up:
        assert not tall.contains_wordform(form)
        for size in (grande, venti):
            assert size.contains_wordform(form)

    for form in exclusively_in_venti:
        for size in (tall, grande):
            assert not size.contains_wordform(form)

        assert venti.contains_wordform(form)


@pytest.fixture
def paradigm_manager(coffee_layout_dir: Path, identity_transducer):
    return ParadigmManager(coffee_layout_dir, identity_transducer)


@pytest.fixture
def coffee_layout_dir(testdata: Path) -> Path:
    """
    Returns the layout directory containing:
     - has-multiple-sizes -- coffee-inspired sizes
     - has-only-one-size
    """
    return testdata / "layouts"


@pytest.fixture
def testdata() -> Path:
    testdata_path = Path(__file__).parent / "testdata"
    assert testdata_path.is_dir()
    return testdata_path


@pytest.fixture
def identity_transducer() -> Transducer:
    return IdentityTransducer()


class IdentityTransducer:
    """
    For each lookup, returns the query unchanged -- .lookup() is the identity function.

    Note: ${lemma} is substituted BEFORE calling .bulk_lookup(), so the "analysis" will
    just be whatever is in the paradigm cell, with all the substitutions finished.
    """

    def bulk_lookup(self, analyses: Iterable[str]) -> dict[str, set[str]]:
        result = {}
        for analysis in analyses:
            result[analysis] = {self.lookup(analysis)}
        return result

    @staticmethod
    def lookup(analysis: str) -> str:
        return analysis


def distinct_permutation(sequence):
    """
    Returns a permutation of the given sequence that is guaranteed to not be the same
    order as the given input.
    """
    assert len(sequence) > 1, "there is no distinct permutation for this input"
    original = list(sequence)
    result = original.copy()

    while result != original:
        random.shuffle(result)
    return result

