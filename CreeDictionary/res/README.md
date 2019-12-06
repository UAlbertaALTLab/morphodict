# Data files

> Convenient variable `utils.shared_res_dir` is a `pathlib.Path` object that refers to this directory

# `test_db_words.txt`

newline separated cree words that goes into `test_db.sqlite3`

Comments should be added using preceding hash sign.

Empty lines are allowed and will be ignored

After editing the file `$ USE_TEST_DB=true manage-db build-test-db [-m|--multi-processing N]` to rebuild the test database.