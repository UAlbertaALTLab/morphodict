#!/bin/sh

# expected to be called from pipfile
# "$@" passes additional arguments to the shell script

if [ $# -lt 1 ] ; then
  echo "error: not enough arguments"
  echo "Usage: import.sh [-i] path/to/dictionaries/"
  exit 1
fi

if [ "$USE_TEST_DB" = "True" ] || [ "$USE_TEST_DB" = "true" ]; then
  echo "Please set USE_TEST_DB=False to use db.sqlite3"
  exit 1
fi

set -e

DB_FILE=CreeDictionary/db.sqlite3
if [ -f "$DB_FILE" ]; then
  rm -i $DB_FILE
fi

echo "Creating db.sqlite3 from scratch..."

"$(dirname "$0")"/remake-api-migrations.sh

pipenv run python CreeDictionary/manage.py migrate

manage-db import "$@"