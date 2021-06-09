import re
from pathlib import Path
from typing import Iterable

import pytest

from CreeDictionary.CreeDictionary.paradigm.manager import ONLY_SIZE, ParadigmManager


def test_one_size(paradigm_manager: ParadigmManager):
    assert set(paradigm_manager.sizes_of("has-only-one-size")) == {ONLY_SIZE}

    paradigm = paradigm_manager.paradigm_for(
        "has-only-one-size", lemma="everything bagel"
    )
    assert paradigm is not None

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


@pytest.fixture
def paradigm_manager():
    testdata = Path(__file__).parent / "testdata"
    assert testdata.exists()
    transducer = IdentityTransducer()
    return ParadigmManager(testdata / "layouts", transducer)


class IdentityTransducer:
    """
    For each lookup, returns the query unchanged (.lookup() is the identity function).
    """

    def bulk_lookup(self, analyses: Iterable[str]) -> dict[str, set[str]]:
        result = {}
        for analysis in analyses:
            result[analysis] = {self.lookup(analysis)}
        return result

    @staticmethod
    def lookup(analysis: str) -> str:
        return analysis
