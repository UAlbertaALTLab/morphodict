import random

from django.db import transaction
from hypothesis import given, example, assume
from hypothesis._strategies import composite, integers, just
from hypothesis.extra.django import from_model
import pytest
from API.models import Inflection
from DatabaseManager.xml_importer import import_crkeng_xml
from constants import LexicalCategory, LC
from tests.conftest import (
    random_inflections,
    inflections_of_category,
    analyzable_inflections,
)

# https://github.com/pytest-dev/pytest-django/issues/514#issuecomment-497874174
from utils import hfstol_analysis_parser


# weird: setting scope to "module" will let the tests in creefuzzySearcher_tests/search_tests.py access the contaminated database
# setting scope to "function" removes that effect. while introduces overheads for tests in this file. (re-imported the xml for every test function)
@pytest.fixture(scope="function")
def hundredth_test_database(crk_eng_hundredth_file, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with transaction.atomic():
            import_crkeng_xml(crk_eng_hundredth_file, verbose=False)
            yield


@pytest.mark.django_db
@given(inflection=random_inflections())
def test_stuff(inflection: Inflection, hundredth_test_database):
    cat = hfstol_analysis_parser.extract_category(inflection.analysis)
    if cat is not None:
        if inflection.as_is:
            assert inflection.is_category(cat) is None
        else:
            assert inflection.is_category(cat)


@pytest.mark.django_db
@given(inflection=from_model(Inflection, as_is=just(False)))
def test_malformed_inflection_analysis_field(inflection: Inflection):
    assume(hfstol_analysis_parser.extract_category(inflection.analysis) is None)
    with pytest.raises(ValueError):
        inflection.is_category(LC.VTA)


@pytest.mark.django_db
def test_lemma_fetching_by_analysis():
    lemma = Inflection(
        id=0,
        text="yôtinipahtâw",
        analysis="yôtinipahtâw+V+AI+Ind+Prs+3Sg",
        as_is=False,
        is_lemma=True,
    )
    lemma.save()

    fetched_lemmas = Inflection.fetch_non_as_is_lemmas_by_fst_analysis(
        "yôtinipahtâw+V+AI+Ind+Prs+3Sg"
    )
    assert fetched_lemmas[0].id == 0

    fetched_lemmas = Inflection.fetch_non_as_is_lemmas_by_fst_analysis("A+B+C")
    assert fetched_lemmas == []
