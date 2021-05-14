from datetime import timedelta
from os.path import dirname
from pathlib import Path

import pytest
from CreeDictionary.API.models import Wordform
from hypothesis import settings
from hypothesis.strategies import SearchStrategy

settings.register_profile("default", deadline=timedelta(milliseconds=5000))
# otherwise it's possible to get DeadlineExceed exception cuz each test function runs too long
# see error report here
# https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary/jobs/637122984?utm_medium=notification&utm_source=github_status

settings.load_profile("default")


@pytest.fixture(scope="session")
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


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
    Strategy to return lemmas from the database.
    """
    return WordformStrategy(is_lemma=True, as_is=False)
