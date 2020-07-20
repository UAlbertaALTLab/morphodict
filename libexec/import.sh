# expected to be called from pipfile
# 0001 is the basis of the import script in Database Manager
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

pipenv run python CreeDictionary/manage.py migrate API 0001

manage-db import "$@"

pipenv run python CreeDictionary/manage.py migrate
