from pathlib import Path

import pytest
from more_itertools import first, ilen

from CreeDictionary.paradigm.manager import ParadigmManager


def test_generates_demonstrative_paradigm(paradigm_manager) -> None:
    paradigm = paradigm_manager.paradigm_for("niya+Pron+Pers+1Sg")
    assert paradigm is not None
    assert paradigm.contains_wordform("niya")
    assert paradigm.contains_wordform("kiya")
    assert paradigm.contains_wordform("wiya")

    assert ilen(paradigm.panes) == 1
    pane = first(paradigm.panes)


@pytest.fixture
def paradigm_manager(shared_datadir: Path) -> ParadigmManager:
    from shared import expensive

    layout_dir = shared_datadir / "paradigm-layouts"
    assert layout_dir.is_dir()
    assert (layout_dir / "static").is_dir()
    assert (layout_dir / "dynamic").is_dir()
    return ParadigmManager(layout_dir, expensive.strict_generator)
