"""
Unit tests for the paradigm pane module.
"""
from more_itertools import one

from CreeDictionary.CreeDictionary.paradigm.panes import Pane, \
    CompoundRow


def test_compound_rows():
    pane = Pane.parse("_ Tag\t${lemma}\n")
    row = one(pane.rows)

    multiple_forms = ("form", "longer-form")

    filled_row = row.fill({"${lemma}": multiple_forms})
    assert isinstance(filled_row, CompoundRow)

    for form in multiple_forms:
        assert filled_row.contains_wordform(form)
