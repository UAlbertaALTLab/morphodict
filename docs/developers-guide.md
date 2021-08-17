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

If you run into trouble, the following notes may help:

  - On Ubuntu 20.04, if pipenv can’t find Python 3.9 and complains about
    there being `no module named distutils.command`, do `apt install -y
    python3-distutils`

  - On Ubuntu, if you get an error running pipenv that says `"Python.h" not
    found`, install the `python3.9-dev` package

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
DEBUG_PARADIGM_TABLES=true
```

These are environment variables that affect whether Django is in debug mode
and whether Django should use a smaller test database.

The environment variables go into effect when using `pipenv shell`, or by
running a program with `pipenv run`. However, `pytest` is configured to
always `USE_TEST_DB`, regardless of the `.env` file contents.

### The development environment

Run `pipenv shell` so that all of the Python dependencies work:

    pipenv shell

### Run the bootstrap script

Running

    ./scripts/dev-bootstrap

creates the test databases for all supported languages.

### Full database

Where to get a full dictionary is described in [Dictionary
data](dictionary_data).

Now import the dictionaries into the database:

    ./${sssttt}-manage importjsondict [file]

As the current import code has not been optimized at all, for a full
dictionary this can take half an hour even on a machine that is quite fast,
and longer on slow ones.

### Compile JavaScript and CSS

Our JavaScript and CSS must be built before being used. Run this
command:

    npm run build

(note: using foreman automatically runs the underlying command in watch
mode)


Running the development server
------------------------------

Install foreman with `gem install --user foreman`.

Then run `foreman start` to run the Django servers for all languages, as
well as the Rollup watch process.

Then you can access the dictionary applications at various port numbers:

 - itwêwina: <http://127.0.0.1:8000/>
 - arpeng: <http://127.0.0.1:8007/>
 - cwdeng: <http://127.0.0.1:8005/>
 - srseng: <http://127.0.0.1:8009/>

Because [cookies are not port-specific for historical insecurity
reasons](https://stackoverflow.com/questions/1612177/are-http-cookies-port-specific),
you can only be logged in to one `127.0.0.1` development site at a time. If
that becomes problematic, give each development site a unique hostname by
adding the following to `/etc/hosts`:

    127.0.0.1 arpeng-local
    127.0.0.1 cwdeng-local
    127.0.0.1 crkeng-local
    127.0.0.1 srseng-local

Then you can access the sites with cookie isolation at
<http://crkeng-local:8000/>, <http://cwdeng-local:8005/>,
<http://arpeng-local:8007/>, and so on.

If you only want to run one dictionary, you can locally comment out lines
in the Procfile.

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
