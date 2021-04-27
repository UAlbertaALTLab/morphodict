"""
Test parsing panes.
"""

from pathlib import Path

import pytest

from CreeDictionary.paradigm.panes import (
    ColumnLabel,
    EmptyCell,
    HeaderRow,
    InflectionCell,
    MissingForm,
    Pane,
    ParadigmTemplate,
    Row,
    RowLabel,
)


def test_parse_na_paradigm(na_layout_path: Path):
    """
    Parses the Plains Cree NA paradigm.

    This paradigm has three panes:
     - basic (no header)
     - diminutive (two rows: a header and one row of content)
     - possession

    With possession having the most columns.
    """
    with na_layout_path.open(encoding="UTF-8") as layout_file:
        na_paradigm_template = ParadigmTemplate.load(layout_file)

    assert count(na_paradigm_template.panes()) == 3
    basic_pane, diminutive_pane, possession_pane = na_paradigm_template.panes()

    assert basic_pane.header is None
    assert basic_pane.num_columns == 2
    assert diminutive_pane.num_columns == 2
    assert count(diminutive_pane.rows()) == 2
    assert possession_pane.header
    assert possession_pane.num_columns == 4


@pytest.mark.parametrize("cls", [EmptyCell, MissingForm])
def test_singleton_classes(cls):
    """
    A few classes should act like singletons.
    """
    assert cls() is cls()
    assert cls() == cls()


def sample_pane():
    return Pane(
        [
            HeaderRow(("Der/Dim",)),
            Row([EmptyCell(), ColumnLabel(["Sg"]), ColumnLabel(["Obv"])]),
            Row([RowLabel("1Sg"), MissingForm(), InflectionCell("${lemma}+")]),
        ]
    )


@pytest.mark.parametrize(
    "component",
    [
        EmptyCell(),
        MissingForm(),
        InflectionCell("${lemma}"),
        InflectionCell("ôma+Ipc"),
        ColumnLabel(("Sg",)),
        RowLabel(("1Sg",)),
        HeaderRow(("Imp",)),
        Row([EmptyCell(), ColumnLabel(["Sg"]), ColumnLabel(["Pl"])]),
        Row([RowLabel("1Sg"), MissingForm(), InflectionCell("${lemma}+Pl")]),
        sample_pane(),
    ],
)
def test_str_produces_parsable_result(component):
    """
    Parsing the stringified component should result in an equal component.
    """
    stringified = str(component)
    parsed = type(component).parse(stringified)
    assert component == parsed
    assert stringified == str(parsed)


@pytest.fixture
def na_layout_path(shared_datadir: Path) -> Path:
    """
    Return the path to the NA layout in the test fixture dir.
    NOTE: this is **NOT** the NA paradigm used in production!
    """
    p = shared_datadir / "paradigm-layouts" / "NA.tsv"
    assert p.exists()
    return p


def count(it):
    """
    Returns the number of items iterated in the paradigm
    """
    return sum(1 for _ in it)
