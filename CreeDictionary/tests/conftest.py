from datetime import timedelta
from os.path import dirname
from pathlib import Path

import pytest
from API.models import Wordform
from DatabaseManager.xml_importer import import_xmls
from django.core.management import call_command
from hypothesis import assume, settings
from hypothesis.strategies import SearchStrategy, composite, integers, sampled_from

settings.register_profile("default", deadline=timedelta(milliseconds=5000))
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


class WordformStrategy(SearchStrategy[Wordform]):
    """
    Strategy that fetches Wordform objects from the database LAZILY.

    The query isn't executed until the first example requested.

    NOTE: This is NOT reproducible given a random seed,
    because of its reliance on the database engine's random sort.
    """

    def __init__(self, **filter_args):
        # random elements:
        self._query_set = Wordform.objects.filter(**filter_args).order_by("?")

    def _next(self):
        if not hasattr(self, "_iterator"):
            self._iterator = iter(self._query_set)
        return next(self._iterator)

    def do_draw(self, data) -> Wordform:
        return self._next()

    def calc_is_cacheable(self, recur):
        return False


def lemmas():
    """
    Strategy to return lemmas from the database
    """
    return WordformStrategy(is_lemma=True, as_is=False)


def migrate_and_import(dictionary_dir):
    """
    assuming a fresh in memory database
    migrate to 0005 and import the xml
    """
    call_command("migrate", "API", "0005")
    import_xmls(dictionary_dir, multi_processing=1)
