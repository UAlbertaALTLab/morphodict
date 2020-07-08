from shared import shared_res_dir
from utils import ParadigmSize, WordClass
from utils.paradigm_layout_combiner import import_layouts


def test_import_layouts_na_basic(shared_datadir) -> None:
    imported_layout = import_layouts(shared_datadir / "layouts")
    assert imported_layout[WordClass.NA, ParadigmSize.BASIC] == [
        ['"One"', "=N+A+Sg"],
        ['"Many"', "=N+A+Pl"],
        ['"Further"', "=N+A+Obv"],
        ["", ""],
        ["", ': "Ownership"'],
        ["", ': "One"'],
        ['"my"', "=N+A+Px1Sg+Sg"],
        ['"your (one)"', "=N+A+Px2Sg+Sg"],
        ["", ': "Further"'],
        ['"his/her"', "=N+A+Px3Sg+Obv"],
        ["", ""],
        ["", ': "Smaller/Lesser/Younger"'],
        ['"One"', "Der/Dim+N+A+Sg"],
    ]
