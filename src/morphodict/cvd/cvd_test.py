import random

import pytest

from morphodict.lexicon.models import Wordform, Definition
from morphodict.cvd import extract_keyed_words
from morphodict.cvd.definition_keys import (
    definition_to_cvd_key,
    cvd_key_to_wordform_query,
)

FAKE_WORD_SET = {"loose", "leaf", "paper", "news_paper", "you're", "that"}


@pytest.mark.parametrize(
    ("query", "words"),
    [
        (
            "paper",
            ["paper"],
        ),
        ("  PAPER!", ["paper"]),
        # Square brackets come from parenthetical parts of Arok's definitions,
        # so we want to ignore them when extracting keys to do the cosine vector search.
        (" paper, (loose!) [yes]", ["paper", "loose"]),
        (
            "loose-leaf paper",
            ["loose", "leaf", "paper"],
        ),
        ("news-paper", ["news_paper"]),
        # not in FAKE_WORD_SET:
        ("cheese", []),
        ("Cheese-Paper", ["paper"]),
        ("that's", ["that"]),
        ("you're", ["you're"]),
    ],
)
def test_extract_words(query, words):
    assert extract_keyed_words(query, keys=FAKE_WORD_SET) == words


@pytest.mark.parametrize(
    ("slug", "expect_null_analysis"),
    [
        ("maskwa", False),
        ("awa@p", False),
        ("pôni-", True),
    ],
)
def test_definition_keys(slug, expect_null_analysis, db):
    """
    The definition vectors have to store a unique key on disk that uniquely
    identifies a wordform, even if the database is re-imported. This tests the
    function for getting the original wordform back from a database query.

    One issue that came with the xml→importjson move was that some analyses
    could now be null, so we explicitly test that case.
    """
    for d in Definition.objects.filter(
        auto_translation_source__isnull=True, wordform__slug=slug
    ):
        assert (d.wordform.raw_analysis is None) == expect_null_analysis

        cvd_key = definition_to_cvd_key(d)
        kwargs = cvd_key_to_wordform_query(cvd_key)
        wordforms = Wordform.objects.filter(**kwargs)
        assert wordforms.count() == 1
        assert wordforms.get() == d.wordform
