from pathlib import Path

import pytest
from django.core.management import call_command
from django.db import IntegrityError
from pytest_django.fixtures import _django_db_helper
from pytest_django.plugin import DjangoDbBlocker

from morphodict.lexicon.models import (
    Wordform,
    TargetLanguageKeyword,
    SourceLanguageKeyword,
)

TESTDATA_DIR = Path(__file__).parent / "testdata"

# Helpers


def import_test_file(filename, reimport=False, **command_kwargs):
    """
    Helper to run `importjsondict`.

    If `reimport` is True, the file is imported twice to allow checking for
    whether re-running an import does anything unexpected.
    """

    def do_import():
        call_command(
            "importjsondict",
            skip_building_vectors_because_testing=True,
            json_file=TESTDATA_DIR / filename,
            **command_kwargs,
        )

    do_import()
    if reimport:
        print("re-running import")
        do_import()


def definitions_match(definition_objects, expected_descriptor):
    """
    Return whether Definition objects have expected properties.

    The order of the definitions, and their sources, may appear in any order.

    expected_descriptor is a shorthand format, consisting of a list or tuple
    `(definition_string, sources)` where `sources` may be a single string for a
    single source, or a list of strings for multiple sources.
    """

    # We want to do set comparisons. But to put things inside sets, we have to
    # first make them hashable by freezing them.
    comparable_actual = set(
        (defn.text, frozenset(c.abbrv for c in defn.citations.all()))
        for defn in definition_objects
    )
    comparable_expected = set(
        (e[0], frozenset(e[1] if isinstance(e[1], list) else [e[1]]))
        for e in expected_descriptor
    )

    return comparable_actual == comparable_expected


def parametrize_reimport(f):
    """
    DRY helper decorator for wordy parametrization
    """
    return pytest.mark.parametrize("reimport", [False, True], ids=["", "reimport"])(f)


def parametrize_translate_wordforms(f):
    """
    DRY helper decorator for wordy parametrization
    """
    return pytest.mark.parametrize(
        "translate_wordforms", [True, False], ids=["translate", "no-translate"]
    )(f)


def parametrize_incremental(f):
    """
    DRY helper decorator for wordy parametrization
    """
    return pytest.mark.parametrize(
        "incremental", [False, True], ids=["", "incremental"]
    )(f)


@pytest.fixture(scope="class")
def class_scoped_db(request: pytest.FixtureRequest, django_db_blocker: DjangoDbBlocker):
    """A class-scoped DB fixture

    The normal pytest-django `db` fixture is function-scoped, meaning that it
    gets torn down and set up again for every test case in a class.

    This reproduces the core bits of that with class scope, allowing a class
    with multiple tests in which the same DB transaction is used for all tests
    in the class.
    """
    pass


# Tests


@parametrize_reimport
@parametrize_translate_wordforms
def test_import_lemma_without_auto_translation(db, translate_wordforms, reimport):
    import_test_file(
        "single-word.importjson",
        translate_wordforms=translate_wordforms,
        reimport=reimport,
    )

    if not translate_wordforms:
        assert Wordform.objects.count() == 1
        assert Wordform.objects.filter(text="maskwak").count() == 0
    else:
        assert Wordform.objects.count() > 10

    lemma = Wordform.objects.get(slug="maskwa")
    assert lemma
    assert lemma.paradigm == "NA"
    assert lemma.text == "maskwa"
    assert lemma.raw_analysis == [[], "maskwa", ["+N", "+A", "+Sg"]]
    assert lemma.is_lemma

    lemma_definitions = list(lemma.definitions.all())
    assert len(lemma_definitions) == 2

    assert definitions_match(
        lemma_definitions, [["A bear.", "MD"], ["bear, black bear", "CW"]]
    )

    target_kws = list(TargetLanguageKeyword.objects.all())
    assert set(kw.text for kw in target_kws) == {"black", "bear"}
    assert all(kw.wordform == lemma for kw in target_kws)

    # Since everything here was fully analyzable, there shouldn’t be any extra
    # indexing.
    assert SourceLanguageKeyword.objects.count() == 0


def debug(wf):
    print(repr(wf))
    for d in wf.definitions.all():
        print(f"  {d.text} {d.source_ids}")


@parametrize_reimport
def test_import_lemma_auto_translation(db, reimport):
    import_test_file("single-word.importjson", reimport=reimport)

    debug(Wordform.objects.get(slug="maskwa"))

    plural_wf = Wordform.objects.get(text="maskwak")
    debug(plural_wf)
    assert definitions_match(
        plural_wf.definitions.all(),
        [["bears.", "🤖MD"], ["bears, black bears", "🤖CW"]],
    )

    for d in plural_wf.definitions.all():
        source = d.auto_translation_source
        assert source is not None
        assert d.citations.first().abbrv == "🤖" + source.citations.first().abbrv


@parametrize_reimport
@parametrize_translate_wordforms
def test_import_lemma_auto_translation_with_multiple_sources(
    db, translate_wordforms, reimport
):
    import_test_file(
        "lemma-with-multiple-definition-sources.importjson",
        translate_wordforms=translate_wordforms,
        reimport=reimport,
    )

    wf = Wordform.objects.get(slug="amisk")
    assert definitions_match(wf.definitions.all(), [["beaver", ["MD", "CW"]]])

    if translate_wordforms:
        plural_wf = Wordform.objects.get(text="amiskwak")
        assert definitions_match(
            plural_wf.definitions.all(), [["beavers", ["🤖MD", "🤖CW"]]]
        )


@parametrize_reimport
class TestSourceLanguageKeywordPopulation:
    @pytest.fixture(autouse=True)
    def setup(self, db, settings, reimport):
        settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT = True

        import_test_file(
            "items-needing-source-language-keywords.importjson", reimport=reimport
        )

    def test_indexing_of_non_matching_slug(self):
        """
        When the slug does not match the text of an analyzable wordform, make
        sure the slug gets indexed so that it is searchable.
        """

        wf = Wordform.objects.get(slug="amisk2")

        kw = SourceLanguageKeyword.objects.get(wordform=wf)
        assert kw.text == "amisk2"

    def test_indexing_of_unanalyzable_form(self):
        """
        Usually the FST handles finding the lemma for a source-language search;
        that doen’t work when the FST doesn’t know about a term.

        ‘maskwa’ is of course analyzable but in the test data for this test, no
        analysis is given in the importjson.
        """

        wf = Wordform.objects.get(slug="maskwa")

        kw = SourceLanguageKeyword.objects.get(wordform=wf)
        assert kw.text == "maskwa"

        kw2 = TargetLanguageKeyword.objects.get(wordform=wf)
        assert kw2.text == "bear"

    def test_indexing_of_fst_lemma(self):
        wf = Wordform.objects.get(slug="kôkom_")
        assert SourceLanguageKeyword.objects.get(text="kôkom")


@pytest.mark.parametrize("model", [SourceLanguageKeyword, TargetLanguageKeyword])
def test_uniqueness_constraints_on_target_language_keyword(db, model):
    """
    Not super-important, but try to save a bit of space by not re-indexing the
    same keyword for the same wordform.
    """
    import_test_file("single-word.importjson")

    wf = Wordform.objects.first()

    model.objects.create(wordform=wf, text="foo")
    with pytest.raises(IntegrityError, match="UNIQUE constraint failed"):
        model.objects.create(wordform=wf, text="foo")


@parametrize_incremental
@parametrize_translate_wordforms
def test_defns_updated(db, translate_wordforms, incremental):
    import_test_file(
        "single-word.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(), [["A bear.", "MD"], ["bear, black bear", "CW"]]
    )

    if translate_wordforms:
        plural_wf = Wordform.objects.get(text="maskwak")
        assert definitions_match(
            plural_wf.definitions.all(),
            [["bears.", "🤖MD"], ["bears, black bears", "🤖CW"]],
        )

    import_test_file(
        "updated-single-word-defns.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(), [["bear", ["CW", "MD"]], ["black bear", "CW"]]
    )

    if translate_wordforms:
        plural_wf = Wordform.objects.get(text="maskwak")
        assert definitions_match(
            plural_wf.definitions.all(),
            [["bears", ["🤖CW", "🤖MD"]], ["black bears", "🤖CW"]],
        )


@parametrize_incremental
@parametrize_translate_wordforms
def test_entry_changed(db, translate_wordforms, incremental):
    import_test_file(
        "paradigm-change-before.importjson",
        translate_wordforms=True,
        incremental=incremental,
    )

    lemma = Wordform.objects.get(slug="miýotêhêw")
    assert lemma.paradigm == "VAI"
    assert definitions_match(
        lemma.definitions.all(),
        [
            ["He has a good heart (for people).", "MD"],
            ["s/he is good-hearted, s/he has a good heart", "CW"],
        ],
    )

    if translate_wordforms:
        inflected_wf = Wordform.objects.get(text="kimiýotêhânâwâw")
        assert inflected_wf.lemma == lemma
        assert definitions_match(
            inflected_wf.definitions.all(),
            [
                ["you all have a good heart.", "🤖MD"],
                ["you all are good-hearted, you all have a good heart", "🤖CW"],
            ],
        )

    import_test_file(
        "paradigm-change-after.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    lemma = Wordform.objects.get(slug="miýotêhêw")
    assert lemma.paradigm == "VTA"
    assert definitions_match(
        lemma.definitions.all(),
        [
            [
                "s/he gives s.o. a good feeling at heart",
                "CW",
            ]
        ],
    )

    if translate_wordforms:
        inflected_wf = Wordform.objects.get(text="kimiýotêhâwâwak")
        assert inflected_wf.lemma == lemma
        assert definitions_match(
            inflected_wf.definitions.all(),
            [
                [
                    "you all give them a good feeling at heart",
                    "🤖CW",
                ],
            ],
        )


def test_running_without_translations_after_running_with_removes_stuff(db):
    import_test_file("paradigm-change-before.importjson", translate_wordforms=True)

    assert Wordform.objects.count() > 10
    assert Wordform.objects.get(slug="miýotêhêw")

    import_test_file("paradigm-change-before.importjson", translate_wordforms=False)

    assert Wordform.objects.count() == 1
    assert Wordform.objects.get(slug="miýotêhêw")


@parametrize_incremental
def test_defn_added(db, incremental):
    import_test_file("single-word.importjson", incremental=incremental)

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(), [["A bear.", "MD"], ["bear, black bear", "CW"]]
    )

    import_test_file("single-word-defn-added.importjson", incremental=incremental)

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(),
        [
            ["A bear.", "MD"],
            ["bear, black bear", "CW"],
            ["new defn", ["CW", "MD", "XYZ"]],
        ],
    )


@parametrize_incremental
def test_defn_removed(db, incremental):
    import_test_file("single-word-defn-added.importjson", incremental=incremental)

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(),
        [
            ["A bear.", "MD"],
            ["bear, black bear", "CW"],
            ["new defn", ["CW", "MD", "XYZ"]],
        ],
    )

    import_test_file("single-word.importjson", incremental=incremental)

    lemma = Wordform.objects.get(slug="maskwa")
    assert definitions_match(
        lemma.definitions.all(), [["A bear.", "MD"], ["bear, black bear", "CW"]]
    )


@parametrize_incremental
def test_entry_added(db, incremental):
    import_test_file("single-word.importjson", incremental=incremental)

    assert Wordform.objects.filter(is_lemma=True).count() == 1
    assert Wordform.objects.get(slug="maskwa")

    import_test_file("two-words.importjson", incremental=incremental)

    assert Wordform.objects.filter(is_lemma=True).count() == 2
    assert Wordform.objects.get(slug="maskwa")
    amisk = Wordform.objects.get(slug="amisk")

    assert definitions_match(amisk.definitions.all(), [["beaver", ["MD", "CW"]]])


@parametrize_incremental
def test_entry_removed(db, incremental):
    import_test_file("two-words.importjson", incremental=incremental)

    assert Wordform.objects.filter(is_lemma=True).count() == 2
    assert Wordform.objects.get(slug="maskwa")
    amisk = Wordform.objects.get(slug="amisk")

    assert definitions_match(amisk.definitions.all(), [["beaver", ["MD", "CW"]]])

    import_test_file("single-word.importjson", incremental=incremental, purge=True)

    assert Wordform.objects.filter(is_lemma=True).count() == 1
    assert Wordform.objects.get(slug="maskwa")


@parametrize_incremental
@parametrize_translate_wordforms
def test_non_lemma_wordform_added(db, translate_wordforms, incremental):
    import_test_file(
        "single-word.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    assert Wordform.objects.filter(is_lemma=True).count() == 1
    assert Wordform.objects.get(slug="maskwa")

    if translate_wordforms:
        assert (
            Wordform.objects.get(text="maskwak")
            .definitions.filter(auto_translation_source_id__isnull=True)
            .count()
            == 0
        )
    else:
        assert Wordform.objects.count() == 1

    import_test_file(
        "single-word-plus-wordform.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    wf = Wordform.objects.get(text="maskwak")
    assert definitions_match(
        wf.definitions.filter(auto_translation_source__isnull=True),
        [["bears", "X"]],
    )


@parametrize_incremental
@parametrize_translate_wordforms
def test_non_lemma_wordform_removed(db, translate_wordforms, incremental):
    import_test_file(
        "single-word-plus-wordform.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
    )

    wf = Wordform.objects.get(text="maskwak")
    assert definitions_match(
        wf.definitions.filter(auto_translation_source__isnull=True),
        [["bears", "X"]],
    )

    import_test_file(
        "single-word.importjson",
        translate_wordforms=translate_wordforms,
        incremental=incremental,
        purge=True,
    )

    assert Wordform.objects.filter(is_lemma=True).count() == 1
    assert Wordform.objects.get(slug="maskwa")

    if translate_wordforms:
        assert (
            Wordform.objects.get(text="maskwak")
            .definitions.filter(auto_translation_source_id__isnull=True)
            .count()
            == 0
        )
    else:
        assert Wordform.objects.count() == 1


@parametrize_translate_wordforms
def test_non_lemma_definition(db, translate_wordforms):
    assert Wordform.objects.count() == 0

    import_test_file(
        "non-lemma-definition.importjson", translate_wordforms=translate_wordforms
    )

    lemma = Wordform.objects.get(slug="nîmiw")
    non_lemma = Wordform.objects.get(text="nîminâniwan")

    assert non_lemma.lemma == lemma

    assert non_lemma.raw_analysis == [[], "nîmiw", ["+V", "+AI", "+Ind", "+X"]]

    expected_defns = [["it is a dance, a time of dancing", "CW"]]
    if translate_wordforms:
        expected_defns.append(["people dance", "🤖CW"])
    assert definitions_match(non_lemma.definitions.all(), expected_defns)

    assert {"time", "danc"}.issubset(
        {t.text for t in TargetLanguageKeyword.objects.filter(wordform=non_lemma)}
    )
