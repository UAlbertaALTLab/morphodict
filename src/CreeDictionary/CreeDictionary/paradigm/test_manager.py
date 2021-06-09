from pathlib import Path
from unittest.mock import MagicMock

import pytest

from CreeDictionary.CreeDictionary.paradigm.manager import ParadigmManager, ONLY_SIZE


def test_one_size(paradigm_manager: ParadigmManager):
    assert set(paradigm_manager.sizes_of("has-only-one-size")) == {ONLY_SIZE}


@pytest.mark.xfail
def test_multiple_sizes(paradigm_manager: ParadigmManager):
    assert set(paradigm_manager.sizes_of("has-multiple-sizes")) == {
        "tall", "grande", "venti"
    }


@pytest.fixture
def paradigm_manager():
    testdata = Path(__file__).parent / "testdata"
    assert testdata.exists()
    transducer = MagicMock()
    transducer.bulk_lookup = MagicMock(side_effect=NotImplementedError)
    return ParadigmManager(testdata / "layouts", transducer)
