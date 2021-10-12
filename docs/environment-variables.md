# Environment variables

These values can be set to tweak morphodict’s runtime behaviour.

You can set these environment variables directly on the command-line using
the standard method for your shell. But it is common to set them in a
`.env` file instead, where various tools will automatically pick them up.

However, all of pipenv, foreman, and our django setup will read from the
`.env` file. These different bits of code have different rules for whether
to prefer a value from the existing environment or from the `.env` file,
and because they can set environment variables based on the `.env` file,
they override each other’s default logic in complicated ways.

For that reason, when changing any of these values, the safest way to
ensure that the changes take effect is to make the change in the `.env`
file, exit from the `pipenv shell` environment, and start a new `pipenv
shell`.

## DEBUG

Django magical variable. This defaults to the production setting `False`.
You should add `DEBUG=False` to the `.env` file in development.

## ENABLE_DJANGO_DEBUG_TOOLBAR

Whether to enable the [Django debug toolbar]. If unset, the default
depends on whether `DEBUB` is on, and whether the code is running on
`CI`. Since you probably want to use debugging tools when `DEBUG` is on,
it's enabled if `DEBUG` is enabled; however, this toolbar is _slow_ and
may interfere with end-to-end tests.

Set `ENABLE_DJANGO_DEBUG_TOOLBAR=False` to disable it in your dev
environment!

The debug toolbar is **always disabled** on production and in CI.

[Django debug toolbar]: https://github.com/jazzband/django-debug-toolbar

## USE_TEST_DB

It specifies whether to use `test_db.sqlite3` instead of `db.sqlite3`. It defaults to production setting "False". you should add `USE_TEST_DB=True` in .env file.

Note: Python unit tests always use a test database.

(DEBUG_PARADIGM_TABLES)=

## DEBUG_PARADIGM_TABLES

When this environment variable is set to True, both layout files and
`altlabel.tsv` are re-read on every page load. This is extremely convenient
when editing paradigm layout or label files, as you don’t need to
constantly restart the server to see the effects of your changes.

## LOG_LEVEL

You can set this to `DEBUG` to see a lot more info about what Django is
doing behind the scenes.

## QUERY_LOG_LEVEL

You can set this to `DEBUG` to have Django print out all the SQL statements
it runs, for debugging purposes.
