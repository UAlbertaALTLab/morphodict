from datetime import timedelta
from os.path import dirname
from pathlib import Path

import pytest
from hypothesis import settings

from morphodict.lexicon.models import Wordform

settings.register_profile("default", deadline=timedelta(milliseconds=5000))
# otherwise it's possible to get DeadlineExceed exception cuz each test function runs too long
# see error report here
# https://travis-ci.org/UAlbertaALTLab/morphodict/jobs/637122984?utm_medium=notification&utm_source=github_status

settings.load_profile("default")


@pytest.fixture(scope="session")
def topmost_datadir() -> Path:
    return Path(dirname(__file__)) / "data"


@pytest.fixture(params={"is_lemma": True, "raw_analysis__isnull": False})
def lemmas(db):
    """
    Strategy to return lemmas from the database.

    It fetches Wordform objects from the database LAZILY.

    The query isn't executed until the first example requested.

    NOTE: This is NOT reproducible given a random seed,
    because of its reliance on the database engine's random sort.
    """

    return iter(
        Wordform.objects.filter(is_lemma=True, raw_analysis__isnull=False).order_by("?")
    )


@pytest.fixture
def lemma(db, lemmas) -> Wordform:
    return next(lemmas)
