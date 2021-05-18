Developer’s Guide
=================

Use this guide to work on the **Cree Intelligent Dictionary** repo.


Installing for the first time
-----------------------------

Clone the repo and `cd` into it, as usual.

    git clone https://github.com/UAlbertaALTLab/cree-intelligent-dictionary.git
    cd cree-intelligent-dictionary

### Install Python

Get Python 3.9 and [Pipenv](https://github.com/pypa/pipenv#installation).

Within the directory, install all Python dependencies:

    pipenv install --dev

### Install NodeJS

Install [NodeJS][] version 10 or greater.

[NodeJS]: https://nodejs.org/

With Node installed, install all of the JavaScript dependencies using `npm`:

    npm install

### Environment

Create a file named `.env` in the project root using the following
template:

```sh
# .env
DEBUG=true
USE_TEST_DB=true
```

These are environment variables that affect whether Django is in debug
mode and whether Django should use `./CreeDictionary/test_db.sqlite3`
instead of the full `db.sqlite3` which must be built from
non-redistributable files.

The environment variables go into effect when using `pipenv shell`, or by
running a program with `pipenv run`. However, `pytest` is configured to
always `USE_TEST_DB`, regardless of the `.env` file contents.

### The development environment

Run `pipenv shell` so that all of the Python dependencies work:

    pipenv shell

### Full database

> Note: if you have `USE_TEST_DB=true`, you can skip this

Download `crkeng.xml` and place it under `CreeDictionary/res/dictionaries/`

These files are copyright protected and not allowed on GitHub. Ask
coworkers about the ‘altlab’ repo.

If you do not have access to the full `crkeng.xml`, set `USE_TEST_DB=false`
and use the excerpt in this repository at
`CreeDictionary/res/test_dictionaries/crkeng.xml`.

As is the custom with Django app, migrations are used to initialize the
schema. Apply them with

    ./CreeDictionary/manage.py migrate

Now import the dictionaries into the database:

    ./CreeDictionary/manage.py xmlimport CreeDictionary/res/dictionaries/crkeng.xml

This typically takes 10-15 minutes on the full dictionary.

### Compile JavaScript and CSS

Our JavaScript and CSS must be built before being used. Run this
command:

    npm run build

(note: this is always run via `npm start`)


Running the development server
------------------------------

    npm start

This starts both the Django server, and the Rollup watch process.

 - Homepage: <http://127.0.0.1:8000/>


Where are the JavaScript files?
-------------------------------

They're located in `frontend/`. They're compiled by [Rollup][] to the
appropriate static directory. Note that Rollup allows you to `import` or
`require()` npm modules in to the frontend JavaScript code; use this
power wisely!

Rollup also minifies the JavaScript when `DEBUG=False`.


Where are the CSS files?
-------------------------------

They're located in `frontend/css`.  They're compiled by [Rollup][] to the
appropriate static directory. We're using [PostCSS][] to inline
any `@import`'d CSS, and to provide a fallback for
[CSS custom properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*) (a.k.a., CSS Variables).

Rollup/PostCSS also minifies the CSS when `DEBUG=False`.


Unit Tests
----------

    pipenv run test

It recognizes the following:

 - The Django settings module in `setup.cfg` (for `pytest-django` to work)
 - `--doctest-modules` `--mypy` in `Pipfile [script]` (to enable doctest and Mypy tests)
 - `DEBUG=False` `USE_TEST_DB=True` in `.env`


Cypress integration tests
-------------------------

    npm test

Or, for interactive use:

    npx cypress open

> **Eddie “sez”**: My workflow is to have three terminals open:
>
> 1. Vim (editing files)
> 2. `npm start` — start the development server
> 3. `npx cypress open` — start Cypress interactively 
>

Profiling Code
--------------

We use [django-toolbar-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/). 
It provides great UI for stack tracing and SQL query profiling.

![django debug toolbar](images/django-debug-toolbar.png)


Format Python code
------------------

We format all Python code with [Black](https://black.readthedocs.io/en/stable/)

To run it on all of the files:

    pipenv run format

> **Protip**! Make this a part of your git pre-commit hook!

Optional: Install HFST
----------------------

You don’t need this to run the dictionary, but having these tools installed
can be useful if you are building, modifying, or directly interacting with
FSTs.

On Mac:

>     brew install UAlbertaALTLab/hfst/hfst

On Windows:

> Download [hfst-latest.zip](https://apertium.projectjj.com/win32/nightly/)
> and unpack it. Add the `hfst/bin` folder to your system path.

On Linux:

>     sudo apt-get install -y hfst

For help, see [HFSTOL installation guide](https://github.com/hfst/hfst#installation-packages-for-debian-and-ubuntu).


<!-- links -->

[Rollup]: https://rollupjs.org/guide/en/
[PostCSS]: https://postcss.org/
