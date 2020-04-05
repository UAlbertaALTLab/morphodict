import pytest

from API.models import Wordform
from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import load_engcrk_xml, find_latest_xml_files
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
@pytest.mark.xfail(
    reason="fst is updated. Need a new example that generates multiple spellings"
)
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
@pytest.mark.xfail(reason="fst changed, new examples needed")
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    """
    test purpose: sometimes two entries in the xml produce the same analysis. Their definition shouldn't be merged
    """

    migrate_and_import(shared_datadir / "crkeng-small-common-analysis-different-lc")
    assert Wordform.objects.get(text="pisin").definitions.count() == 1

    # Note: this test no longer works because pisin and pisiniw no longer produces the same analysis

    # We need to find two entries in the xml that produces the same analysis. See
    # DatabaseManager_tests/data/crkeng-small-common-analysis-different-lc/crkeng.xml

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


@pytest.mark.parametrize(
    "file_names,expected_crkeng_index,expected_engcrk_index",
    [
        # should use un-timestamped files if necessary
        (["crkeng.xml", "engcrk.xml"], 0, 1),
        # should use un-timestamped files if necessary but timestamped files take higher precedence
        (["crkeng.xml", "engcrk.xml", "engcrk_cw_md_200113.xml"], 0, 2),
        # should compare timestamps
        (
            [
                "crkeng_200314.xml",
                "engcrk_200419.xml",
                "crkeng_200112.xml",
                "engcrk_200114.xml",
            ],
            0,
            1,
        ),
        # irrelevant files should not matter
        (
            [
                "crkeng_200314.xml",
                "engcrk_200419.xml",
                "crkeng_200112.xml",
                "engcrk_200114.xml",
                "README.md",
            ],
            0,
            1,
        ),
    ],
)
def test_find_latest_xml_files(
    tmp_path_factory, file_names, expected_crkeng_index, expected_engcrk_index
):
    temp_dir = tmp_path_factory.mktemp("foo")
    for file_name in file_names:
        (temp_dir / file_name).write_text("")
    crkeng_file_path, eng_crk_file_path = find_latest_xml_files(temp_dir)
    assert file_names.index(crkeng_file_path.name) == expected_crkeng_index
    assert file_names.index(eng_crk_file_path.name) == expected_engcrk_index


def test_find_latest_xml_files_no_file_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_latest_xml_files(tmp_path)


# todo: tests for EnglishKeywords
