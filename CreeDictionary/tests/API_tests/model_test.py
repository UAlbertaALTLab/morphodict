import pytest
from hypothesis import given, assume
from hypothesis.strategies import from_regex

from DatabaseManager.__main__ import cmd_entry

# don not remove theses lines. Stuff gets undefined
# noinspection PyUnresolvedReferences
from tests.conftest import one_hundredth_xml_dir, topmost_datadir
from API.models import Inflection
from DatabaseManager.xml_importer import import_xmls
from constants import LC
from tests.conftest import random_inflections, random_lemmas

from utils import fst_analysis_parser


# this very cool fixture provides the tests in this file with a database that's imported from one hundreths of the xml
@pytest.fixture(autouse=True, scope="module")
def hundredth_test_database(one_hundredth_xml_dir, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        import_xmls(one_hundredth_xml_dir, verbose=False)
        yield
        cmd_entry([..., "clear"])


# this cool `random_inflections` draws random inflection from the database
@pytest.mark.django_db
@given(inflection=random_inflections())
def test_extract_category(inflection: Inflection):
    cat = fst_analysis_parser.extract_category(inflection.analysis)
    if cat is not None:
        if inflection.as_is:
            assert inflection.is_category(cat) is None
        else:
            assert inflection.is_category(cat)


@pytest.mark.django_db
@given(inflection=random_inflections())
def test_malformed_inflection_analysis_field(inflection: Inflection):
    inflection.as_is = False
    inflection.analysis = "ijfasdjfie"
    assume(fst_analysis_parser.extract_category(inflection.analysis) is None)
    with pytest.raises(ValueError):
        inflection.is_category(LC.VTA)


#### Tests for Inflection.fetch_lemmas_by_user_query()


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_query_exact_wordform_in_database(lemma: Inflection):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    results = Inflection.fetch_lemma_by_user_query(query)
    assert len(results) >= 1, f"Could not find {query!r} in the database"

    exact_matches = [match for match in results if match.id == lemma.id]
    assert len(exact_matches) >= 1, f"No exact matches for {query!r} in {results}"

    match, *_ = exact_matches
    assert query == match.text


@pytest.mark.django_db
@given(lemma=random_lemmas(), ws=from_regex(r"\s{1,4}", fullmatch=True))
def test_query_with_extraneous_whitespace(lemma: Inflection, ws: str):
    """
    Adding whitespace to a query should not affect the results.
    """
    user_query = lemma.text

    normal_results = Inflection.fetch_lemma_by_user_query(user_query)
    normal_result_ids = set(res.id for res in normal_results)
    assert len(normal_result_ids) >= 1

    query_with_ws = user_query + ws
    results_with_ws = Inflection.fetch_lemma_by_user_query(query_with_ws)
    result_ids_with_ws = set(res.id for res in results_with_ws)
    assert len(result_ids_with_ws) >= 1

    assert normal_result_ids == result_ids_with_ws
