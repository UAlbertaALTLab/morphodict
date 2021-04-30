from more_itertools import first, ilen

from CreeDictionary.paradigm.manager import ParadigmManager


def test_generates_demonstrative_paradigm() -> None:
    layouts = ParadigmManager()
    paradigm = layouts.paradigm_for("niya+Pron+Pers+1Sg")
    assert paradigm is not None
    assert ilen(paradigm.panes) == 1
    assert paradigm.contains_wordform("niya")
    assert paradigm.contains_wordform("kiya")
    assert paradigm.contains_wordform("wiya")
