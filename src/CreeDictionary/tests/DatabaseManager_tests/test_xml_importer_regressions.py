import pytest
from CreeDictionary.API.models import EnglishKeyword, Wordform
from CreeDictionary.tests.DatabaseManager_tests.conftest import migrate_and_import


@pytest.mark.django_db
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-common-analysis-definition-merge")

    query_set = Wordform.objects.filter(text="nipa")

    kill_him_inflections = []
    for inflection in query_set:
        for definition in inflection.definitions.all():
            if "Kill" in definition.text:
                kill_him_inflections.append(inflection)

    assert len(kill_him_inflections) == 1
    kill_him_inflection = kill_him_inflections[0]
    assert kill_him_inflection.pos == "V"


@pytest.mark.django_db
def test_import_pipon_of_different_word_classes(shared_datadir):

    # The Cree word pipon has two entries in the test xml, one's word class is VII and the other's is NI
    migrate_and_import(shared_datadir / "crkeng-pipon-of-different-word-classes")

    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/190
    # Issue description: search results for some inflected form of word pipon is not showing up
    # Cause: pipon lemmas wrongly marked as "as-is" in the database when the xml actually provided enough resolution
    # on the word classes (VII and NI)

    # todo: let `migrate_and_import` report success/ambiguity/no-analysis count so that further tests to the importer
    #   can be easier constructed. e.g. in this case we'll only need to assert `success == 2`

    assert (
        Wordform.objects.filter(text="pipon", is_lemma=True, as_is=False).count() == 2
    )

    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/412
    # Issue description: The verb entry and the noun entry have the same 3 definitions.
    #   while in the source, the noun has 2 definitions:
    #       It is winter.
    #       it is winter; is one year
    #   The verb has 1 definition:
    #       year, winter
    # They are wrongly merged.

    assert (
        Wordform.objects.filter(text="pipon", is_lemma=True, pos="N")
        .get()
        .definitions.all()
        .count()
        == 1
    )
    assert (
        Wordform.objects.filter(text="pipon", is_lemma=True, pos="V")
        .get()
        .definitions.all()
        .count()
        == 2
    )


@pytest.mark.django_db
def test_import_niska(shared_datadir):

    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/213
    # searching with niskak didn't yield an inflection of "niska" as niska wasn't disambiguated and was marked as_is
    migrate_and_import(shared_datadir / "crkeng-niska")

    assert not Wordform.objects.filter(text="niska", is_lemma=True).get().as_is


@pytest.mark.django_db
def test_import_maskwa(shared_datadir):

    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/213
    # searching with maskwak didn't yield an inflection of "maskwa" as "maskwa" wasn't disambiguated and was marked as_is
    migrate_and_import(shared_datadir / "crkeng-maskwa")

    assert not Wordform.objects.filter(text="maskwa", is_lemma=True).get().as_is


@pytest.mark.django_db
def test_import_calgary(shared_datadir):
    """
    See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/353
    """

    # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/213
    # searching with maskwak didn't yield an inflection of "maskwa" as "maskwa" wasn't disambiguated and was marked as_is
    migrate_and_import(shared_datadir / "crkeng-calgary")

    results = EnglishKeyword.objects.filter(text__startswith="calgar")
    assert len(results) >= 1
    assert {"otôskwanihk"} == {r.lemma.text for r in results}
