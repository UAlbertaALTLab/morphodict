from pathlib import Path

import pytest
from django.core.management import call_command

from morphodict.lexicon.models import Wordform

TESTDATA_DIR = Path(__file__).parent / "testdata"


def do_nîmiw_asserts():
    lemma = Wordform.objects.get(slug="nîmiw")
    assert lemma
    assert lemma.paradigm == "VAI"
    assert lemma.text == "nîmiw"
    assert lemma.raw_analysis == [[], "nîmiw", ["+V", "+AI", "+Ind", "+3Sg"]]
    assert lemma.is_lemma

    lemma_definitions = list(lemma.definitions.all())
    assert len(lemma_definitions) == 1
    lemma_defn = lemma_definitions[0]
    assert lemma_defn.source_ids == ["CW"]
    assert lemma_defn.text == "s/he dances"

    wordform = Wordform.objects.get(text="nîminâniwan")
    assert wordform.lemma == lemma
    assert wordform.slug is None
    assert wordform.paradigm is None
    assert wordform.raw_analysis == [[], "nîmiw", ["+V", "+AI", "+Ind", "+X"]]
    assert not wordform.is_lemma
    wordform_definitions = list(
        wordform.definitions.filter(auto_translation_source__isnull=True)
    )
    assert len(wordform_definitions) == 1
    wordform_defn = wordform_definitions[0]
    assert wordform_defn.source_ids == ["CW"]
    assert wordform_defn.text == "it is a dance, a time of dancing"

    auto_definition = wordform.definitions.get(auto_translation_source__isnull=False)
    assert auto_definition.auto_translation_source_id == lemma_defn.id
    assert auto_definition.source_ids == ["auto"]


def test_single_entry_with_wordform(db):
    assert Wordform.objects.count() == 0

    call_command("importjsondict", json_file=TESTDATA_DIR / "single-word.importjson")

    assert Wordform.objects.count() != 0

    do_nîmiw_asserts()

    call_command("importjsondict", json_file=TESTDATA_DIR / "single-word.importjson")

    do_nîmiw_asserts()


@pytest.mark.skip
def test_blah():
    pass


def blah():
    """
    >>> 1 + 1
    NaN
    """
