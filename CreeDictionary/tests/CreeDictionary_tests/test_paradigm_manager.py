from more_itertools import first, ilen

from CreeDictionary.paradigm.manager import default_paradigm_manager


def test_generates_demonstrative_paradigm() -> None:
    layouts = default_paradigm_manager()
    paradigm = layouts.paradigm_for("niya+Pron+Pers+1Sg")
    assert paradigm is not None
    assert paradigm.contains_wordform("niya")
    assert paradigm.contains_wordform("kiya")
    assert paradigm.contains_wordform("wiya")

    assert ilen(paradigm.panes) == 1
    pane = first(paradigm.panes)
