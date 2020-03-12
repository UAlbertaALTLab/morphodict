import pytest

from API.models import Wordform
from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import load_engcrk_xml
from constants import POS
from tests.conftest import migrate_and_import
from utils import shared_res_dir


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-nice-0")

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1


@pytest.mark.django_db
def test_import_xml_lemma_w_multiple_spellings(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-lemma-w-multiple-spelling")

    pisin_lemma = Wordform.objects.filter(text="pisin", is_lemma=True).get()

    assert Wordform.objects.filter(
        text="pisiniw", is_lemma=False, lemma__id=pisin_lemma.id
    ).exists()


@pytest.mark.django_db
def test_import_xml_fst_no_analysis(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-fst-can-not-analyze")
    assert len(Wordform.objects.all()) == 1
    assert Wordform.objects.get(text="miwapisin").as_is is True
    assert Wordform.objects.get(text="miwapisin").is_lemma is True


@pytest.mark.django_db
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-common-analysis-different-lc")
    assert Wordform.objects.get(text="pisin").definitions.count() == 1
    assert Wordform.objects.get(text="pisiniw").definitions.count() == 2


@pytest.mark.django_db
def test_import_xml_crkeng_small_duplicate_l_pos_lc_definition_merge(shared_datadir):
    migrate_and_import(
        shared_datadir / "crkeng-small-duplicate-l-pos-lc-definition-merge"
    )
    assert len(Wordform.objects.get(text="asawâpiwin").definitions.all()) == 3


@pytest.mark.django_db
def test_import_xml_crkeng_small_common_xml_lemma_different_lc(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-common-xml-lemma-should-merge")
    assert len(Wordform.objects.filter(text="pisiw", is_lemma=True)) == 1
    assert (
        Wordform.objects.filter(text="pisiw", is_lemma=True).get().definitions.count()
        == 2
    )


def test_load_engcrk():
    res = load_engcrk_xml(shared_res_dir / "test_dictionaries" / "engcrk.xml")
    # nipâw means "sleep"
    assert "sleep" in res["nipâw", POS.V]


# todo: tests for EnglishKeywords
