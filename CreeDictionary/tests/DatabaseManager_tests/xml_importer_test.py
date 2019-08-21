import pytest

from API.models import Inflection
from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import import_crkeng_xml


# fixme: pytest must have done some magic. The logger will still print to console despite verbose=False is set


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):

    import_crkeng_xml(
        shared_datadir / "crkeng-small-nice-0.xml", multi_processing=1, verbose=False
    )

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Inflection.objects.filter(text=inflection)) >= 1


@pytest.mark.django_db
def test_import_xml_lemma_w_multiple_spellings(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-lemma-w-multiple-spelling.xml",
        multi_processing=1,
        verbose=False,
    )
    assert len(Inflection.objects.filter(text="pisin", is_lemma=True)) == 1
    assert len(Inflection.objects.filter(text="pisiniw", is_lemma=True)) == 1


@pytest.mark.django_db
def test_import_xml_fst_no_analysis(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-fst-can-not-analyze.xml",
        multi_processing=1,
        verbose=False,
    )
    assert len(Inflection.objects.all()) == 1
    assert Inflection.objects.get(text="miwapisin").as_is == True
    assert Inflection.objects.get(text="miwapisin").is_lemma == True


@pytest.mark.django_db
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-common-analysis-different-lc.xml",
        multi_processing=1,
        verbose=False,
    )
    assert len(Inflection.objects.get(text="pisiniw").definition_set.all()) == 2


@pytest.mark.django_db
def test_import_xml_crkeng_small_duplicate_l_pos_lc_definition_merge(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-duplicate-l-pos-lc-definition-merge.xml",
        multi_processing=1,
        verbose=False,
    )
    assert len(Inflection.objects.get(text="asawâpiwin").definition_set.all()) == 3


@pytest.mark.django_db
def test_import_xml_crkeng_small_common_xml_lemma_different_lc(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-common-xml-lemma-different-lc.xml",
        multi_processing=1,
        verbose=False,
    )

    assert len(Inflection.objects.filter(text="pisiw", is_lemma=True)) == 1
    assert (
        len(
            Inflection.objects.filter(text="pisiw", is_lemma=True)
            .get()
            .definition_set.all()
        )
        == 2
    )


#
# @pytest.mark.django_db
# def test_clear_database():
#     clear_database(verbose=False)
