import pytest
from API.models import Wordform
from paradigm import EmptyRowType, InflectionCell, Layout, TitleRow
from utils import ParadigmSize

from CreeDictionary.generate_paradigm import generate_paradigm


@pytest.mark.parametrize(
    "lemma,examples",
    [
        # VTA
        ("wâpamêw", ["wâpamêw", "niwâpamâw", "kiwâpamitin", "ê-wâpamât"]),
        # VAI
        ("nipâw", ["nipâw", "ninipân", "kinipân", "ninipânân"]),
        # VTI
        ("mîcisow", ["mîcisow", "nimîcison", "kimîcison", "ê-mîcisoyit"]),
        # VII
        ("nîpin", ["nîpin", "nîpin", "ê-nîpihk"]),
        # NAD
        ("nôhkom", ["nôhkom", "kôhkom", "ohkoma"]),
        # NID
        ("mîpit", ["mîpit", "nîpit", "kîpit", "wîpit"]),
        # NA
        ("minôs", ["minôs", "minôsak", "minôsa"]),
        # NI
        ("nipiy", ["nipiy", "nipîhk", "ninipiy", "kinipiy"]),
    ],
)
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
