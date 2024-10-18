"""
Test paradigm generation for the itwêwina (crkeng) dictionary.
"""

from more_itertools import first

from morphodict.paradigm.generation import default_paradigm_manager

# mîcisow - s/he eats (basic vocabulary)
from morphodict.paradigm.panes import CompoundRow, RowLabel

VAI_LEMMA = "mîcisow"

MULTIPLE_12PL_FORMS = [
    "kimîcisonaw",  # dialectal
    "kimîcisonânaw",  # more common
]

# These are the forms that are typically taught in a 1st year/2nd year class:
EXPECTED_BASIC_VAI_FORMS = [
    # I eat
    "nimîcison",
    # You (sg) eat
    "kimîcison",
    # They (sg) eats (lemma)
    VAI_LEMMA,
    # We (excl.) eat
    "nimîcisonân",
    # We (incl.) eat
    *MULTIPLE_12PL_FORMS,
    # You (pl) eat
    "kimîcisonâwâw",
    # They (pl) eat:
    "mîcisowak",
    # They (obviative) eat
    "mîcisoyiwa",
]


def test_vai_paradigm() -> None:
    """
    Tests the generation of a VAI paradigm. This tests that elementary verb forms
    exist in the paradigm and that multiple forms are produced for the +12Pl
    independent form.
    """
    manager = default_paradigm_manager()

    name = "VAI"
    size = first(manager.sizes_of(name))
    paradigm = manager.paradigm_for(name, lemma=VAI_LEMMA, size=size)
    first_pane = first(paradigm.panes)

    for form in EXPECTED_BASIC_VAI_FORMS:
        assert first_pane.contains_wordform(form)

    # The +12PL form should contain **at least** two wordforms.
    compound_row = first(row for row in first_pane.rows if isinstance(row, CompoundRow))
    n_rows = compound_row.num_subrows
    for form in MULTIPLE_12PL_FORMS:
        assert compound_row.contains_wordform(form)
    assert n_rows >= 2
    label = first(first(compound_row.subrows).cells)
    assert isinstance(label, RowLabel)
    assert "12Pl" in label.fst_tags
    assert label.row_span == n_rows
