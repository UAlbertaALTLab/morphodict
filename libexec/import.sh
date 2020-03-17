# expected to be called from pipfile
# 0005 was the basis of the import script in Database Manager
# -i makes it interactive, ask user to comfirm before he deletes the old test database
# "$@" passes additional arguments to the shell script
DB_FILE=CreeDictionary/db.sqlite3
if [ -f "$DB_FILE" ]; then
  rm -i $DB_FILE
fi

echo "Creating db.sqlite3 from scratch..."

pipenv run python CreeDictionary/manage.py migrate API 0005

manage-db import "$@"

pipenv run python CreeDictionary/manage.py migrate