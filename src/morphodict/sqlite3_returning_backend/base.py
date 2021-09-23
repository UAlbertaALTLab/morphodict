"""
SQLite `INSERT … RETURNING` support.

This lets you call `bulk_create` and immediately get back the IDs auto-assigned
by the database, instead of having to assign them manually, or issue additional
queries to try to find the new IDs for the objects you just saved.

Backport of a feature which should be released as part of Django 4.0. See:
https://github.com/django/django/commit/98abc0c90e0eb7fe3a71cfa360962cf59605f1d3

In `settings.py`, set this module as the `ENGINE` in `DATBASES`.

Requires SQLite >= 3.35; sadly, that is not currently available in any of the
https://hub.docker.com/_/python/ images, but will be in ubuntu:21.10 shortly.
"""

import sqlite3

from django.db.backends.sqlite3 import base, features, operations


class DatabaseFeatures(features.DatabaseFeatures):
    can_return_columns_from_insert = True
    can_return_rows_from_bulk_insert = True


class DatabaseOperations(operations.DatabaseOperations):
    def fetch_returned_insert_rows(self, cursor):
        """
        Given a cursor object that has just performed an INSERT...RETURNING
        statement into a table, return the list of returned data.
        """
        return cursor.fetchall()

    def return_insert_columns(self, fields):
        # SQLite < 3.35 doesn't support an INSERT...RETURNING statement.
        if not fields:
            return "", ()
        columns = [
            "%s.%s"
            % (
                self.quote_name(field.model._meta.db_table),
                self.quote_name(field.column),
            )
            for field in fields
        ]
        return "RETURNING %s" % ", ".join(columns), ()


class DatabaseWrapper(base.DatabaseWrapper):
    """
    This is the entry point used by Django. See ConnectionHandler.__getitem__.
    """

    def __init__(self, *args, **kwargs):
        assert sqlite3.sqlite_version_info >= (
            3,
            35,
        ), f"sqlite version {sqlite3.sqlite_version} is too old"
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

    features_class = DatabaseFeatures
    ops_class = DatabaseOperations
