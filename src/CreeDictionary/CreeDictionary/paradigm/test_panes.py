"""
Unit tests for the paradigm pane module.
"""

import pytest
from more_itertools import first, ilen, last, one

from CreeDictionary.CreeDictionary.paradigm.panes import (
    CompoundRow,
    EmptyCell,
    MissingForm,
    Pane,
    RowLabel,
    SuppressOutputCell,
    WordformCell,
)


def test_compound_rows():
    pane = Pane.parse("_ Tag\t${lemma}\n")
    row = one(pane.rows)

    multiple_forms = ("form", "longer-form")
    filled_row = row.fill({"${lemma}": multiple_forms})
    assert isinstance(filled_row, CompoundRow)

    # Ensure all generated forms are in there:
    for form in multiple_forms:
        assert filled_row.contains_wordform(form)

    assert (
        filled_row.num_subrows == ilen(filled_row.subrows) == len(multiple_forms)
    ), "expected as many subrows as there are forms"

    first_row_cells = tuple(first(filled_row.subrows).cells)
    assert first(row.cells).fst_tags == first_row_cells[0].fst_tags
    assert first_row_cells[0].row_span == len(multiple_forms)

    first_form = first_row_cells[-1]
    assert isinstance(first_form, WordformCell)
    assert first_form.inflection == multiple_forms[0]

    last_row_cells = tuple(last(filled_row.subrows).cells)
    assert isinstance(last_row_cells[0], SuppressOutputCell)

    last_form = last_row_cells[-1]
    assert isinstance(last_form, WordformCell)
    assert last_form.inflection == multiple_forms[-1]


def test_pane_iterate_tr_rows():
    pane = Pane.parse("_ Tag\t${lemma}\n")
    multiple_forms = ("form", "longer-form")
    filled_pane = pane.fill({"${lemma}": multiple_forms})

    assert ilen(filled_pane.rows) == ilen(pane.rows)
    assert ilen(filled_pane.tr_rows) == len(multiple_forms)


def test_row_label_with_row_span():
    label = RowLabel(("Ebb", "Flow"))
    assert label.row_span == 1

    n = 3  # or any small integer above 1
    new_label = label.with_row_span(n)
    assert new_label.fst_tags == label.fst_tags
    assert new_label.row_span == n


@pytest.mark.parametrize("cell", [MissingForm(), EmptyCell(), SuppressOutputCell()])
def test_filling_singleton_cells(cell):
    """
    Filling certain cells should only return the cell itself.
    """
    assert cell == one(cell.fill({}))
