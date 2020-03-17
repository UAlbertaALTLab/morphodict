# expected to be called from pipfile
# 0005 was the basis of the import script in Database Manager
# -i makes it interactive, ask user to comfirm before he deletes the old test database
# "$@" passes additional arguments to the shell script

if [ "$USE_TEST_DB" = "True" ] || [ "$USE_TEST_DB" = "true" ]; then
  echo "Please set USE_TEST_DB=False to use db.sqlite3"
  exit 1
fi


DB_FILE=CreeDictionary/db.sqlite3
if [ -f "$DB_FILE" ]; then
  rm -i $DB_FILE
fi

echo "Creating db.sqlite3 from scratch..."

pipenv run python CreeDictionary/manage.py migrate API 0005

manage-db import "$@"

pipenv run python CreeDictionary/manage.py migrate