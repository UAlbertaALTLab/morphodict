Directories
===========

This is an EXHAUSTIVE list of all directories in this project. If you're
confused about the purpose of a directory, look here!

All directories in this file are relative to project root.

<!-- Note to documenters: Each directory should start with three hashes! -->

### .github

configuration files that interact with GitHub services

### .github/workflows

workflow (interchangeably, actions) that runs by GitHub Actions service when code pushes to GitHub.

### CreeDictionary

A Django site with _django apps_ inside

### CreeDictionary/API

One of the django apps of our project. It defines click-in-text (our other project) API.

### CreeDictionary/API/migrations

Django Migrations of the API app

Migrations are not used to migrate database on production The only times migrations are needed are when we re-build the
database and create empty tables with `manage.py migrate`

This includes when we manually build test database, and when our unit tests build test in memory database.

0000_initial.py migration is re-generated based on models.py everytime when the database is rebuilt.

This directory is managed by the rebuild script and does not require manual intervention

### CreeDictionary/CreeDictionary

One of the django apps of our project. It's the main part of our online dictionary.

### CreeDictionary/CreeDictionary/static

static files (A django concept) for the CreeDictionary app. They are usually javascripts and images

### CreeDictionary/CreeDictionary/templates

templates (A django concept, usually for HTML) for the CreeDictionary app.

### CreeDictionary/CreeDictionary/static/CreeDictionary

see below

### CreeDictionary/CreeDictionary/templates/CreeDictionary

You might think there is no stupid reason such verbose-looking directories should exist. But it's Django.

### CreeDictionary/API/templatetags

see below

### CreeDictionary/morphodict/templatetags

see below

### CreeDictionary/CreeDictionary/templatetags

defines custom tags you can use in django templates. A tag looks in the form of {{}} or {{ | }} and is a Django feature

### CreeDictionary/DatabaseManager

A python module with a CLI that manages importation of xml files to our db.sqlite3. Not used at runtime.

See more under the directory's README.md about how to use it

### CreeDictionary/DatabaseManager/logs

DatabaseManager outputs logs when it imports xml dictionaries into the database. Here are logs that record details of
what happened to the xml entries during the importation.

### CreeDictionary/morphodict

A django app that has our language invariant components of the project. This is currently a WIP.

### CreeDictionary/morphodict/tests

Tests that belong to morphodict. It's separate from most tests as in the future morphodict might be extracted to a
standalone django app.

### CreeDictionary/res

Data files. See README under the directory to see explanation of its contents.

### CreeDictionary/res/dictionaries

Dictionary files that are not public. This directory's contents are ignored by a local .gitignore

dictionary files are stored in altlab repo at the following place:

`altlab/crk/dicts/crkeng.xml`

They also used to be stored on Sapir server with a timestamp like the following

`crkeng_cw_md_200314.xml`

The last six digits is a timestamp of when this file is built, in the format of yymmdd.

### CreeDictionary/res/fst

Ask your supervisor what an FST is.

### CreeDictionary/res/layouts

Files that determine how paradigm tables in our app look like.

### CreeDictionary/res/lemma_tags

Files here store templates of common lemma analyses for each [word class](./glossary.md#word-class)

i.e.

- NA lemmas usually have tags +N+A+Sg
- VAI lemmas usually have tags +V+AI+Ind+3Sg
- ...

See its local README for a detailed explanation of the motivation and usage behind it.

### CreeDictionary/res/test_dictionaries

A subset of our proper dictionaries. This is loaded in our test database for test purposes. Database generation is
managed by DatabaseManager CLI's.

### CreeDictionary/shared

Expensive initializations / utilities that are shared in multiple places.

### CreeDictionary/tests

Where all tests except morphodict's tests reside.

### CreeDictionary/tests/API_tests

Test for the API django app

### CreeDictionary/tests/CreeDictionary_tests

Test for the CreeDictionary django app

### CreeDictionary/tests/DatabaseManager_tests

Test for the DatabaseManager python module

### CreeDictionary/tests/DatabaseManager_tests/data

Input cases for Database Manager CLI. Minimal examples of test dictionary inputs.

### CreeDictionary/utils

A python module of Utility functions

### CreeDictionary/tests/utils_tests

Tests for the utils module.

### CreeDictionary/tests/utils_tests/data

Test data for the utils module

### CreeDictionary/tests/utils_tests/data/layouts

More test data for the utils module

### cypress

Cypress is our integration testing tool. This is where test scripts and helpers reside.

### cypress/fixtures

Test data for integration tests.

### cypress/fixtures/recording

Test data for integration tests.

### cypress/fixtures/recording/_search

Test data for integration tests.

### cypress/integration

Detailed specification of the tests.

### cypress/support

Our integration test utilities.

### docs

The most important thing in the world

### docs/images

images used in the docs

### libexec

Utility programs that are *usually* dependency free and ran by
developers or automated scripts. The programs here do not need to be
distributed with the main app, but are useful for maintenance tasks (often
run in CI).

Why the name "libexec"? [History](https://refspecs.linuxfoundation.org/FHS_3.0/fhs-3.0.html#usrlibexec).

### src

All our javascripts and css. They eventually are compiled to static folders.

### src/css

All our css. They eventually are compiled to static folders.

### src/css/vendor

"vendor" refers to code originally created by outside sources. For example, `normalize.css` is an external script
that ["makes browsers render all elements more consistently ..."][normalize].

[normalize]: https://necolas.github.io/normalize.css/

### types

Npm package `@altlab/types` with typescript that serve as our API schema.

The typescript file is generated through  CI from python TypedDict's under `CreeDictionary/API/schema.py`

When the source file is changed, be sure to bump the package version. It's OK to forget - 
our CI will check if the package version is bumped when the produced type file has changed. 

Note this package is separate from the "package" under the project root level,
the latter being javascript dependencies of our project.
