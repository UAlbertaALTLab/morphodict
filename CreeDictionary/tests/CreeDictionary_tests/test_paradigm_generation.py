import pytest
from CreeDictionary.generate_paradigm import generate_paradigm
from API.models import Wordform
from paradigm import Layout, EmptyRowType, TitleRow, InflectionCell
from utils import ParadigmSize


@pytest.mark.parametrize("lemma,examples", [
    # VAI
    ("nipâw", ["nipâw", "ninipân", "kinipân",  "ninipânân"]),
    # VTA
    ("wâpamêw", ["wâpamêw", "niwâpamâw", "kiwâpamitin",  "ê-wâpamât"]),
    # TODO: other word classes
])
@pytest.mark.django_db
def test_paradigm(lemma: str, examples: list[str]):
    """
    Test we can generate a paradigm from a given lemma.
    """
    wordform = Wordform.objects.get(text=lemma, is_lemma=True)
    paradigms = generate_paradigm(wordform, ParadigmSize.BASIC)
    for inflection in examples:
        assert paradigms_contain_inflection(paradigms, inflection)


def paradigms_contain_inflection(paradigms: list[Layout], inflection: str) -> bool:
    for paradigm in paradigms:
        for row in paradigm:
            if isinstance(row, (EmptyRowType, TitleRow)):
                continue
            for cell in row:
                if isinstance(cell, InflectionCell) and cell.inflection == inflection:
                    return True
    return False
