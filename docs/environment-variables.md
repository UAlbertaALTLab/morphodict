## Environment variables

These values can be set to tweak morphodict’s runtime behaviour.

### DEBUG

Django magical variable. This defaults to the production setting `False`.
You should add `DEBUG=False` to .env file in development.
Note: `DEBUG` CANNOT be enabled on Sapir!

### ENABLE_DJANGO_DEBUG_TOOLBAR

Whether to enable the [Django debug toolbar]. If unset, the default
depends on whether `DEBUB` is on, and whether the code is running on
`CI`. Since you probably want to use debugging tools when `DEBUG` is on,
it's enabled if `DEBUG` is enabled; however, this toolbar is _slow_ and
may interfere with end-to-end tests.

Set `ENABLE_DJANGO_DEBUG_TOOLBAR=False` to disable it in your dev
environment!

The debug toolbar is **always disabled** on production and in CI.

[Django debug toolbar]: https://github.com/jazzband/django-debug-toolbar

### USE_TEST_DB

It specifies whether to use `test_db.sqlite3` instead of `db.sqlite3`. It defaults to production setting "False". you should add `USE_TEST_DB=True` in .env file.

Note: python unit tests under `CreeDictionary/tests` always creates in memory empty database unless specified 
in the test code otherwise. E.g. `CreeDictionary/tests/API_test/model_test.py` is
 an example configuration where `test_db.sqlite3` is actually used.

(DEBUG_PARADIGM_TABLES)=

### DEBUG_PARADIGM_TABLES

When this environment variable is set to True, both layout files and
`altlabel.tsv` are re-read on every page load. This is extremely convenient
when editing paradigm layout or label files, as you don’t need to
constantly restart the server to see the effects of your changes.
