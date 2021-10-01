# type: ignore
# because there aren’t yet stubs for morphodict_mobile
import os
import shutil
import sqlite3
import sys
import threading
from io import IOBase
from pathlib import Path

import django
from django.core.management import call_command


import morphodict_mobile


def setup_logging():
    """Redirect python stdout+stderr to iOS system log

    This adds timestamps during development, and allows python output to be
    collected later from a device that wasn’t hooked up to Xcode at the time, by
    running `sudo log collect --device`
    """

    class Log(IOBase):
        def __init__(self, name):
            self.name = name

        def write(self, s):
            if not isinstance(s, str):
                s = str(s)
            if s.strip():
                morphodict_mobile.log(self.name + ": " + s)

    sys.stdout = Log("pystdout")
    sys.stderr = Log("pystderr")


def setup_database():
    """Copy the read-only DB file bundled with the app into place

    And do this only if needed.
    """

    bundled_db_file = Path(os.environ["MORPHODICT_BUNDLED_DB"])
    db_directory = Path(os.environ["MORPHODICT_DB_DIRECTORY"])

    target_db_file = db_directory / "db.sqlite3"

    def get_db_metadata(db_file):
        result = {}

        with sqlite3.connect(f"file:{db_file}?immutable=1") as db:
            cursor = db.execute(
                """
                    -- timestamp of last migration
                    SELECT MAX(applied)
                    FROM django_migrations
                """
            )
            result["migration_timestamp"] = cursor.fetchone()[0]

            # The user may be upgrading from a version of the app from before
            # the import timestamp was in the database. In that case, the table
            # does not exist.
            cursor = db.execute(
                """
                    -- timestamp of last migration
                    SELECT COUNT(*)
                    FROM sqlite_master
                    WHERE type = 'table'
                    AND tbl_name = 'lexicon_importstamp'
                """
            )
            has_importstamp = cursor.fetchone()[0] != 0

            if has_importstamp:
                cursor = db.execute(
                    """
                        SELECT MAX(timestamp)
                        FROM lexicon_importstamp
                    """
                )
                result["import_timestamp"] = cursor.fetchone()[0]
            else:
                result["import_timestamp"] = None

        print(f"{db_file}: {result!r}")
        return result

    def should_copy_db_file():
        print("Checking if DB needs to be copied")
        if not target_db_file.is_file():
            return True

        bundled_migration_metadata = get_db_metadata(bundled_db_file)
        target_migration_metadata = get_db_metadata(target_db_file)

        if bundled_migration_metadata == target_migration_metadata:
            return False

        return True

    if should_copy_db_file():
        print("Copying DB file")
        # Presumably we could copy user preferences here too
        shutil.copyfile(bundled_db_file, target_db_file)

    os.environ["DATABASE_URL"] = f"sqlite://{target_db_file}"


setup_logging()
setup_database()

# Save a bit of memory by giving runserver threads 1MiB stacks instead of
# default 8MiB.
threading.stack_size(1024 * 1024)

django.setup()

call_command("runserver", use_reloader=False, addrport="4828", mobile_trigger=True)
