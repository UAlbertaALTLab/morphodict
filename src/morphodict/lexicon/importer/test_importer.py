from pathlib import Path

from django.core.management import call_command

from morphodict.lexicon.models import Wordform

TESTDATA_DIR = Path(__file__).parent / "testdata"


def test_stuff(db):
    assert Wordform.objects.count() == 0

    call_command("importjsondict", json_file=TESTDATA_DIR / "single-word.importjson")

    assert Wordform.objects.count() != 0

    lemma = Wordform.objects.get(slug="nîmiw")
    assert lemma
    wordform = Wordform.objects.get(text="nîminâniwan")

    assert wordform.lemma == lemma
