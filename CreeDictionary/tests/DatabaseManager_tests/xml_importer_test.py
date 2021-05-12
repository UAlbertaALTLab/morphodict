import pytest

from CreeDictionary.API.models import Wordform
from CreeDictionary.DatabaseManager.cree_inflection_generator import expand_inflections
from CreeDictionary.DatabaseManager.xml_importer import find_latest_xml_file
from CreeDictionary.tests.DatabaseManager_tests.conftest import migrate_and_import


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-nice-0")

    expanded = expand_inflections(["yôwamêw+V+TA+Ind+3Sg+4Sg/PlO"], verbose=False)
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1


@pytest.mark.django_db
@pytest.mark.xfail(
    reason="fst is updated. Need a new example that generates multiple spellings"
)
def test_import_lemma_with_multiple_spellings(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-small-lemma-with-multiple-spelling")

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

    migrate_and_import(shared_datadir / "crkeng-small-common-analysis-different-ic")
    assert Wordform.objects.get(text="pisin").definitions.count() == 1

    # Note: this test no longer works because pisin and pisiniw no longer produces the same analysis

    # We need to find two entries in the xml that produces the same analysis. See
    # DatabaseManager_tests/data/crkeng-small-common-analysis-different-ic/crkeng.xml

    assert Wordform.objects.get(text="pisiniw").definitions.count() == 2


@pytest.mark.django_db
def test_import_xml_crkeng_small_common_xml_l_different_ic(shared_datadir):
    # This test shows the behavior of the importer when entries with the same l but different ic in the xml file exists
    # These entries will be identified as belonging to different lemmas

    migrate_and_import(shared_datadir / "crkeng-small-common-xml-l-different-ic")
    assert len(Wordform.objects.filter(text="pisiw", is_lemma=True)) == 2


@pytest.mark.parametrize(
    "file_names,expected_crkeng_index",
    [
        # should use un-timestamped files if necessary
        (["crkeng.xml"], 0),
        # should use un-timestamped files if necessary but timestamped files take higher precedence
        (
            [
                "crkeng_cw_md_200113.xml",
                "crkeng.xml",
            ],
            0,
        ),
        # should compare timestamps
        (
            [
                "crkeng_200314.xml",
                "crkeng_200112.xml",
            ],
            0,
        ),
        # irrelevant files should not matter
        (
            [
                "crkeng_200314.xml",
                "README.md",
                "crkeng_200112.xml",
            ],
            0,
        ),
    ],
)
def test_find_latest_xml_files(tmp_path_factory, file_names, expected_crkeng_index):
    temp_dir = tmp_path_factory.mktemp("foo")
    for file_name in file_names:
        (temp_dir / file_name).write_text("")
    crkeng_file_path = find_latest_xml_file(temp_dir)
    assert file_names.index(crkeng_file_path.name) == expected_crkeng_index


def test_find_latest_xml_files_no_file_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_latest_xml_file(tmp_path)


# todo: tests for EnglishKeywords
