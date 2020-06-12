from datetime import timedelta
from os.path import dirname
from pathlib import Path
from typing import Sequence

import pytest
from API.models import Wordform
from DatabaseManager.xml_importer import import_xmls
from django.core.management import call_command
from hypothesis import assume, settings
from hypothesis.strategies import sampled_from

settings.register_profile("default", deadline=timedelta(milliseconds=5000))
# otherwise it's possible to get DeadlineExceed exception cuz each test function runs too long
# see error report here
# https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary/jobs/637122984?utm_medium=notification&utm_source=github_status

settings.load_profile("default")


@pytest.fixture(scope="session")
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


class LazyWordforms(Sequence[Wordform]):
    """
    Fetches wordforms only when needed.

    The query isn't executed until Hypothesis thinks it's a good idea to do
    so.
    """

    def __init__(self, **filter_args):
        self._query_set = Wordform.objects.filter(**filter_args)

    @property
    def result_set(self) -> tuple:
        if not hasattr(self, "_result_set"):
            self._result_set = tuple(self._query_set)
        return self._result_set

    def __getitem__(self, index) -> Wordform:
        return self.result_set[index]

    def __len__(self) -> int:
        return len(self.result_set)


def lemmas():
    """
    Strategy to return lemmas from the database.
    """
    return sampled_from(LazyWordforms(is_lemma=True, as_is=False))


def migrate_and_import(dictionary_dir):
    """
    assuming a fresh in memory database
    migrate to 0005 and import the xml
    """
    call_command("migrate", "API", "0005")
    import_xmls(dictionary_dir, multi_processing=1)
