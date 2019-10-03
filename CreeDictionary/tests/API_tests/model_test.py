import pytest
from django.db import transaction
from hypothesis import given, assume
from tests.conftest import one_hundredth_xml_dir, topmost_datadir
from API.models import Inflection
from DatabaseManager.xml_importer import import_xmls
from constants import LC
from tests.conftest import random_inflections

# https://github.com/pytest-dev/pytest-django/issues/514#issuecomment-497874174
from utils import hfstol_analysis_parser


# weird: setting scope to "module" will let the tests in creefuzzySearcher_tests/search_tests.py access the contaminated database
# setting scope to "function" removes that effect. while introduces overheads for tests in this file. (re-imported the xml for every test function)
@pytest.fixture(scope="function")
def hundredth_test_database(one_hundredth_xml_dir, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with transaction.atomic():
            import_xmls(one_hundredth_xml_dir, verbose=False)
            yield


# todo: over-engineered and slow. refactor this
@pytest.mark.django_db
@given(inflection=random_inflections())
def test_stuff(inflection: Inflection, hundredth_test_database):
    cat = hfstol_analysis_parser.extract_category(inflection.analysis)
    if cat is not None:
        if inflection.as_is:
            assert inflection.is_category(cat) is None
        else:
            assert inflection.is_category(cat)


# todo: over-engineered and slow. refactor this
@pytest.mark.django_db
@given(inflection=random_inflections())
def test_malformed_inflection_analysis_field(
    inflection: Inflection, hundredth_test_database
):
    inflection.as_is = False
    inflection.analysis = "ijfasdjfie"
    assume(hfstol_analysis_parser.extract_category(inflection.analysis) is None)
    with pytest.raises(ValueError):
        inflection.is_category(LC.VTA)
