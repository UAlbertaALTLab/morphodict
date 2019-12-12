# SAPIR_USER
This affects the username used in ssh commands in `pipenv run pull-db` and `pipenv run push-db`.
You should add SAPIR_USER=your_user_name to .env file.

# DEBUG
Django magical variable. This is default to production setting `False`. You should add `DEBUG=False` to .env file
 in development.
 
 > if you forget to add DEBUG=True, most probably you will get error message `"mod_wsgi" not found`
>. Because the django app mod_wsgi is only required in production.

# USE_TEST_DB

It specifies whether to use `test_db.sqlite3` instead of `db.sqlite3`. It defaults to production setting "False". you should add `USE_TEST_DB=True` in .env file.

Note: python unit tests under `CreeDictionary/tests` always creates in memory empty database unless specified 
in the test code otherwise. E.g. `CreeDictionary/tests/API_test/model_test.py` is
 an example configuration where `test_db.sqlite3` is actually used.