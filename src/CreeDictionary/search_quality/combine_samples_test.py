from io import StringIO
from textwrap import dedent

import pytest

from CreeDictionary.search_quality.combine_samples import iter_results, combine_results


def test_iter_results_works_with_header():
    input_file = StringIO(
        dedent(
            """\
        Query,1,2,3,,Notes
        A,1,,,,Blah
        B,2,3,4,,
        """
        ),
        newline="",
    )
    assert list(iter_results(input_file)) == [
        {"Query": "A", "Values": ["1"]},
        {"Query": "B", "Values": ["2", "3", "4"]},
    ]


def test_iter_results_works_with_header_but_no_notes():
    input_file = StringIO(
        dedent(
            """\
        Query,1,2,3
        A,1,,
        B,2,3,4
        """
        ),
        newline="",
    )
    assert list(iter_results(input_file)) == [
        {"Query": "A", "Values": ["1"]},
        {"Query": "B", "Values": ["2", "3", "4"]},
    ]


def test_iter_results_works_without_header():
    input_file = StringIO(
        dedent(
            """\
        A,1,2
        B,a,b,c,d,e,f,g,h
        """
        ),
        newline="",
    )
    assert list(iter_results(input_file)) == [
        {"Query": "A", "Values": ["1", "2"]},
        {"Query": "B", "Values": ["a", "b", "c", "d", "e", "f", "g", "h"]},
    ]


def test_iter_results_raises_on_duplicate_entry():
    input_file = StringIO(
        dedent(
            """\
        Query,1,2,3,,Notes
        A,1,,,,Blah
        A,2,3,4,,
        """
        ),
        newline="",
    )
    with pytest.raises(Exception, match="Duplicate"):
        list(iter_results(input_file))


def test_iter_results_raises_if_no_gap_before_notes():
    input_file = StringIO(
        dedent(
            """\
        Query,1,2,3,,Notes
        A,1,,,,Blah
        B,2,3,4,x,
        """
        ),
        newline="",
    )
    with pytest.raises(Exception, match="Must have blank column"):
        list(iter_results(input_file))


def test_iter_results_raises_if_more_columns_than_headers():
    input_file = StringIO(
        dedent(
            """\
        Query,1,2,3,,Notes
        A,1,,,,Blah
        B,2,3,4,,,q
        """
        ),
        newline="",
    )
    with pytest.raises(Exception, match="More entries.*than header values"):
        list(iter_results(input_file))


def test_combine_results_pick_top_when_all_agree():
    assert combine_results(
        [["bar", "baz", "qux"], ["bar", "baz", "qux"], ["bar", "baz", "qux"]]
    ) == ["bar", "baz", "qux"]


def test_combine_results_use_voting_for_disagreement():
    assert combine_results(
        [["baz", "bar", "qux"], ["bar", "baz", "qux"], ["bar", "baz", "qux"]]
    ) == ["bar", "baz", "qux"]


def test_combine_results_use_voting_for_disagreement2():
    # This matches the current survey man: a word in #2 position wins if also
    # mentioned in #3 position on another list, versus a word only mentioned in
    # a single list.
    assert combine_results([["bar"], ["bar", "baz"], ["bar", "qux", "baz"]]) == [
        "bar",
        "baz",
        "qux",
    ]
