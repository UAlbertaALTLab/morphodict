Developer’s Guide
=================

Use this guide to work on the **Cree Intelligent Dictionary** repo.


Installing for the first time
-----------------------------

Clone the repo and `cd` into it, as usual.

    git clone https://github.com/UAlbertaALTLab/cree-intelligent-dictionary.git
    cd cree-intelligent-dictionary

Get Python 3.6 and [Pipenv](https://github.com/pypa/pipenv#installation).

Within the directory, install all Python dependencies:

    pipenv install --dev


### Install HFST

Make sure `hfst-optimized-lookup` is a recognizable command on the terminal

On Linux:

>     sudo apt-get install -y hfst

On Mac:

>     brew install UAlbertaALTLab/hfst/hfst

On Windows:

> Download hfstol binary file. Add bin folder to system path.

For help, see [HFSTOL installation guide](https://github.com/hfst/hfst#installation-packages-for-debian-and-ubuntu).


### XML Dictionary Files

Download `crkeng.xml` and `engcrk.xml` and place them under `CreeDictionary/res/dictionaries/`

These files are copyright protected and not allowed on GitHub. Ask coworkers or download from production server under the same directory. On Sapir, the directory is `/opt/cree-intelligent-dictionary/CreeDictionary/res/dictionaries/`

### Environment

Create a file named `.env` under project root with `DEBUG=true` and `USE_TEST_DB=true`.
(Required for both both by npm and pipenv).


### The development environment

Run `pipenv shell` so that all of the Python dependencies work:

    pipenv shell

### Initialize Database

As with any Django app, you must create and apply all migrations.

    pipenv run make-migrations && pipenv run migrate

### Build Database

Now import the dictionaries into the database:

    manage-db import CreeDictionary/res/dictionaries/

It takes several minutes to process the XML file and write into the
database. For better performance, enable multi-processing with
`PROCESS_COUNT` being at most your CPU core count:

    manage-db import CreeDictionary/res/dictionaries/ --muti-processing PROCESS_COUNT

### Create an admin account (optional)

To use the Django admin interface, you need to make yourself an admin
account:

    python ./CreeDictionary/manage.py createsuperuser


Running the development server
------------------------------

    npm start

This starts both the Django server, and the Rollup watch process.

 - Homepage: <http://127.0.0.1:8000/>
 - Admin: <http://127.0.0.1:8000/admin>


Where are the JavaScript files?
-------------------------------

They're located in `src/`. They're compiled by [Rollup][] to the
appropriate static directory. Note that Rollup allows you to `import` or
`require()` npm modules in to the frontend JavaScript code; use this
power wisely!

Rollup also minifies the JavaScript when `DEBUG=False`.


Where are the CSS files?
-------------------------------

They're located in `src/css`.  They're compiled by [Rollup][] to the
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
 - `DEBUG=False` in `.env`


Cypress integration tests
-------------------------

    npm test

Or, for interactive use:

    npx cypress open


Profiling Code
--------------

    pipenv run profile <script_name>

...with `<script_name>` being one of the scripts from `profiling`
folder.


### Example

    pipenv run profile word_search.py

You can come up with profiling scripts yourself.


Format Python code
------------------

We format all Python code with [Black](https://black.readthedocs.io/en/stable/)

To run it on all of the files:

    pipenv run format

> **Protip**! Make this a part of your git pre-commit hook!


<!-- links -->

[Rollup]: https://rollupjs.org/guide/en/
[PostCSS]: https://postcss.org/
