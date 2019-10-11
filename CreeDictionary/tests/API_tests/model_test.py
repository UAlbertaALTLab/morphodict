import pytest
from hypothesis import given, assume

from DatabaseManager.__main__ import cmd_entry

# don not remove theses lines. Stuff gets undefined
# noinspection PyUnresolvedReferences
from tests.conftest import one_hundredth_xml_dir, topmost_datadir
from API.models import Inflection
from DatabaseManager.xml_importer import import_xmls
from constants import LC
from tests.conftest import random_inflections

# https://github.com/pytest-dev/pytest-django/issues/514#issuecomment-497874174
from utils import hfstol_analysis_parser


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
    cat = hfstol_analysis_parser.extract_category(inflection.analysis)
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
    assume(hfstol_analysis_parser.extract_category(inflection.analysis) is None)
    with pytest.raises(ValueError):
        inflection.is_category(LC.VTA)
