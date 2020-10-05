# should be called from pipfile

# -i makes it interactive, ask user to comfirm before he deletes the database
# "$@" passes extra arguments to subcommand build-test-db

DB_FILE=CreeDictionary/test_db.sqlite3
if [ -f "$DB_FILE" ]; then
  rm -i $DB_FILE
fi

set -e

echo "Creating test_db.sqlite3 from scratch..."

"$(dirname "$0")"/remake-api-migrations.sh

pipenv run python CreeDictionary/manage.py migrate

manage-db build-test-db "$@"
