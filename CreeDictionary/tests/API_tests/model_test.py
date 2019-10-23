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


#### Tests for Inflection.fetch_lemmas_by_user_query()


@pytest.mark.django_db
@given(lemma=random_lemmas())
def test_query_exact_wordform_in_database(lemma: Inflection):
    """
    Sanity check: querying a lemma by its EXACT text returns that lemma.
    """

    query = lemma.text
    analysis_to_lemmas, _ = Inflection.fetch_lemma_by_user_query(query)

    exact_match = False
    matched_lemma_count = 0
    for analysis, lemmas in analysis_to_lemmas.items():
        for matched_lemma in lemmas:
            if matched_lemma.id == lemma.id:
                exact_match = True
            matched_lemma_count += 1

    assert matched_lemma_count >= 1, f"Could not find {query!r} in the database"
    assert exact_match, f"No exact matches for {query!r} in {analysis_to_lemmas}"
