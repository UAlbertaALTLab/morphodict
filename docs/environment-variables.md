# DEBUG

Django magical variable. This defaults to the production setting `False`.
You should add `DEBUG=False` to .env file in development.
Note: `DEBUG` CANNOT be enabled on Sapir!

# USE_TEST_DB

It specifies whether to use `test_db.sqlite3` instead of `db.sqlite3`. It defaults to production setting "False". you should add `USE_TEST_DB=True` in .env file.

Note: python unit tests under `CreeDictionary/tests` always creates in memory empty database unless specified 
in the test code otherwise. E.g. `CreeDictionary/tests/API_test/model_test.py` is
 an example configuration where `test_db.sqlite3` is actually used.

# RUNNING_ON_SAPIR

Whether we're running on `sapir.artsrn.ualberta.ca`. There are various
hacks required to make this run properly on Sapir, which are
conditionally enabled using this flag. Note, that if unspecified, the
app will try to determine if it's running on Sapir automatically, by
querying the system's hostname.

It is recommend that you leave this environment variable **unset**.
 
> if you set `RUNNING_ON_SAPIR` to True, you most probably will get the error message `"mod_wsgi" not found`
> because the Django app `mod_wsgi` is only required on Sapir.
