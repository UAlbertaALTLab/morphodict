from datetime import timedelta
from os.path import dirname
from pathlib import Path
from itertools import cycle

import pytest
from hypothesis import settings
from hypothesis.strategies import SearchStrategy, builds

from morphodict.lexicon.models import Wordform

settings.register_profile("default", deadline=timedelta(milliseconds=5000))
# otherwise it's possible to get DeadlineExceed exception cuz each test function runs too long
# see error report here
# https://travis-ci.org/UAlbertaALTLab/morphodict/jobs/637122984?utm_medium=notification&utm_source=github_status

settings.load_profile("default")


@pytest.fixture(scope="session")
def topmost_datadir() -> Path:
    return Path(dirname(__file__)) / "data"


def wordforms(**filter_args) -> SearchStrategy[Wordform]:
    """
    Strategy that fetches Wordform objects from the database LAZILY.

    The query isn't executed until the first example requested.

    NOTE: This is NOT reproducible given a random seed,
    because of its reliance on the database engine's random sort.
    """
    query_set = Wordform.objects.filter(**filter_args).order_by("?")
    iterator = cycle(iter(query_set))

    def strategy():
        return next(iterator)

    return builds(strategy)


def lemmas() -> SearchStrategy[Wordform]:
    """
    Strategy to return lemmas from the database.
    """
    return wordforms(is_lemma=True, raw_analysis__isnull=False)
