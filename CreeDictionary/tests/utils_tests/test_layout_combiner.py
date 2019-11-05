from constants import LC, ParadigmSize
from paradigm import EmptyRow, RowWithContent
from shared import shared_res_dir
from utils.paradigm_layout_combiner import import_layouts


def test_import_layouts_na_basic():
    imported_layout = import_layouts(shared_res_dir / "layouts")
    assert imported_layout[LC.NA, ParadigmSize.BASIC] == [
        RowWithContent(['"One"', "=N+A+Sg"]),
        RowWithContent(['"Many"', "=N+A+Pl"]),
        RowWithContent(['"Further"', "=N+A+Obv"]),
        EmptyRow,
        RowWithContent(["", ': "Smaller/Lesser/Younger"']),
        RowWithContent(['"One"', "Der/Dim+N+A+Sg"]),
        EmptyRow,
        RowWithContent(["", ': "Ownership"']),
        RowWithContent(["", ': "One"']),
        RowWithContent(['"my"', "=N+A+Px1Sg+Sg"]),
        RowWithContent(['"your (one)"', "=N+A+Px2Sg+Sg"]),
        RowWithContent(["", ': "Further"']),
        RowWithContent(['"his/her"', "=N+A+Px3Sg+Obv"]),
    ]
