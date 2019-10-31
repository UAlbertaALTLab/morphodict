from shared import shared_res_dir
from utils.paradigm_layout_combiner import import_layouts
from constants import LC, ParadigmSize


def test_import_layouts_na_basic():
    imported_layout = import_layouts(shared_res_dir / "layouts")
    assert imported_layout[LC.NA, ParadigmSize.BASIC] == [
        ['"One"', "=N+A+Sg"],
        ['"Many"', "=N+A+Pl"],
        ['"Further"', "=N+A+Obv"],
        ["", ""],
        ["", ': "Smaller/Lesser/Younger"'],
        ['"One"', "Der/Dim+N+A+Sg"],
        ["", ""],
        ["", ': "Ownership"'],
        ["", ': "One"'],
        ['"my"', "=N+A+Px1Sg+Sg"],
        ['"your (one)"', "=N+A+Px2Sg+Sg"],
        ["", ': "Further"'],
        ['"his/her"', "=N+A+Px3Sg+Obv"],
    ]
