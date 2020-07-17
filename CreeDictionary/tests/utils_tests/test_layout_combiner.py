from shared import shared_res_dir
from utils import ParadigmSize, WordClass
from utils.paradigm_layout_combiner import import_layouts


def test_import_layouts_na_basic(shared_datadir) -> None:
    imported_layout = import_layouts(shared_datadir / "layouts")
    assert imported_layout[WordClass.NA, ParadigmSize.BASIC] == [
        ['"One"', "${lemma}+N+A+Sg"],
        ['"Many"', "${lemma}+N+A+Pl"],
        ['"Further"', "${lemma}+N+A+Obv"],
        ["", ""],
        ["", ': "Smaller/Lesser/Younger"'],
        ['"One"', "${lemma}+N+A+Der/Dim+N+A+Sg"],
        ["", ""],
        ["", ': "Ownership"'],
        ["", ': "One"'],
        ['"my"', "${lemma}+N+A+Px1Sg+Sg"],
        ['"your (one)"', "${lemma}+N+A+Px2Sg+Sg"],
        ["", ': "Further"'],
        ['"his/her"', "${lemma}+N+A+Px3Sg+Obv"],
    ]
