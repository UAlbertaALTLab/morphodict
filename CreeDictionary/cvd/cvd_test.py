import random

import pytest

from CreeDictionary.API.models import Definition, Wordform
from CreeDictionary.cvd import extract_keyed_words
from CreeDictionary.cvd.definition_keys import (
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
        (" paper, (loose!) [yes]", ["paper", "loose"]),
        (
            "loose-leaf paper",
            ["loose", "leaf", "paper"],
        ),
        ("news-paper", ["news_paper"]),
        ("cheese", []),
        ("Cheese-Paper", ["paper"]),
        ("that's", ["that"]),
        ("you're", ["you're"]),
    ],
)
def test_extract_words(query, words):
    assert extract_keyed_words(query, keys=FAKE_WORD_SET) == words


@pytest.mark.django_db
def test_definition_keys():
    d = random.choice(Definition.objects.filter(auto_translation_source__isnull=True))
    cvd_key = definition_to_cvd_key(d)
    kwargs = cvd_key_to_wordform_query(cvd_key)
    wordforms = Wordform.objects.filter(**kwargs)
    assert wordforms.count() == 1
    assert wordforms.get() == d.wordform
