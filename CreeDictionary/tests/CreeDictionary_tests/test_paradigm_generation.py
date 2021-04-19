import pytest
from CreeDictionary.generate_paradigm import generate_paradigm
from API.models import Wordform
from paradigm import Layout, EmptyRowType, TitleRow, InflectionCell
from utils import ParadigmSize


@pytest.mark.django_db
def test_paradigm():
    """
    Test we can generate a paradigm from a given lemma.
    """
    nipaw = Wordform.objects.get(text="nipâw", is_lemma=True)
    nipaw_paradigm = generate_paradigm(nipaw, ParadigmSize.BASIC)
    assert paradigms_contain_inflection(nipaw_paradigm, "ninipân")
    assert paradigms_contain_inflection(nipaw_paradigm, "kinipân")
    assert paradigms_contain_inflection(nipaw_paradigm, "nipâw")
    assert paradigms_contain_inflection(nipaw_paradigm, "ninipânân")


def paradigms_contain_inflection(paradigms: list[Layout], inflection: str) -> bool:
    for paradigm in paradigms:
        for row in paradigm:
            if isinstance(row, (EmptyRowType, TitleRow)):
                continue
            for cell in row:
                if isinstance(cell, InflectionCell) and cell.inflection == inflection:
                    return True
    return False
