from contextlib import contextmanager

import pytest
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_databases, teardown_databases
from pytest_django.lazy_django import get_django_version

from API.models import Wordform
from DatabaseManager.__main__ import cmd_entry
from DatabaseManager.cree_inflection_generator import expand_inflections


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    cmd_entry([..., "import", str(shared_datadir / "crkeng-small-nice-0")])

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1
