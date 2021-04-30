import pytest
from CreeDictionary.paradigm.manager import ParadigmManager


def test_generates_demonstrative_paradigm() -> None:
    layouts = ParadigmManager()
    paradigm = layouts.paradigm_for("niya+Pron+Pers+1Sg")
    assert paradigm