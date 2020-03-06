from contextlib import contextmanager
from os.path import dirname
from pathlib import Path
from typing import Optional

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
    cmd_entry(
        [..., "import", str(shared_datadir / "crkeng-small-nice-0"), "--no-input"]
    )

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1


def test_replace_db():
    def get_use_new_xml_migration_files():
        return list(migration_dir.glob("*_use_new_xml_files.py"))

    migration_dir = Path(dirname(__file__)) / ".." / ".." / "API" / "migrations"
    original_count = len(get_use_new_xml_migration_files())
    print(migration_dir.absolute())
    cmd_entry([..., "replace"])
    assert len(get_use_new_xml_migration_files()) == original_count + 1

    # clean up
    newest_file_number: Optional[int] = None
    for file in get_use_new_xml_migration_files():
        file_number = int(file.stem[:4])
        if newest_file_number is None or file_number > newest_file_number:
            newest_file_number = file_number
    newest_file = Path(migration_dir / f"{newest_file_number:04d}_use_new_xml_files.py")
    assert "def import_new_dictionaries" in newest_file.read_text()

    # clean up
    newest_file.unlink()
