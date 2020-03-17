from datetime import timedelta
from os.path import dirname
from pathlib import Path

import pytest
from django.core.management import call_command
from hypothesis import assume
from hypothesis.strategies import composite, integers, sampled_from

from API.models import Wordform


from hypothesis import settings

from DatabaseManager.xml_importer import import_xmls

settings.register_profile("default", deadline=timedelta(milliseconds=2000))
# otherwise it's possible to get DeadlineExceed exception cuz each test function runs too long
# see error report here
# https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary/jobs/637122984?utm_medium=notification&utm_source=github_status

settings.load_profile("default")


@pytest.fixture(scope="session")
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


@composite
def analyzable_inflections(draw) -> Wordform:
    """
    inflections with as_is field being False, meaning they have an analysis field from fst analyzer
    """
    inflection_objects = Wordform.objects.all()

    pk_id = draw(integers(min_value=1, max_value=inflection_objects.count()))
    the_inflection = inflection_objects.get(id=pk_id)
    assume(not the_inflection.as_is)
    return the_inflection


@composite
def random_inflections(draw) -> Wordform:
    """
    hypothesis strategy to supply random inflections
    """
    inflection_objects = Wordform.objects.all()
    id = draw(integers(min_value=1, max_value=inflection_objects.count()))
    return inflection_objects.get(id=id)


@composite
def random_lemmas(draw) -> Wordform:
    """
    Strategy that supplies wordforms that are also lemmas!
    """
    lemmas = Wordform.objects.filter(is_lemma=True, as_is=False)
    return draw(sampled_from(list(lemmas)))


def migrate_and_import(dictionary_dir):
    """
    assuming a fresh in memory database
    migrate to 0005 and import the xml
    """
    call_command("migrate", "API", "0005")
    import_xmls(dictionary_dir, multi_processing=1)
