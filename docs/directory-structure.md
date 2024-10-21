# Directory structure

This is a proposal for a new physical layout of the source code in this
repo, meant to replace the somewhat ad-hoc layout of early 2021, in order
to:

  - Allow generalization to more languages than Plains Cree, and

  - Address some other issues that have arisen with the source code layout.

## High-level decisions / assumptions

  - In the file system, dictionary applications such as itwêwina are named
    `sssttt`, where `sss` and `ttt` are each three-letter [ISO 639-3
    language codes][639-3] for the dictionary [source language and target
    language](glossary.md), respectively. Example: `crkeng`.

    The use of a technical abbreviation means that nobody will ever be
    blocked from starting a dictionary for a new language pair on on
    naming/branding questions.

  - There will be at most one intelligent dictionary application for each
    language pair. The code already supports multiple dictionary sources
    within one application, such as both the *Cree: Words* and Maskwacîs
    dictionaries for Plains Cree.

  - Each site will be an independently deployed django project, and have an
    independent database.

    There are advantages and disadvantages to having a single django
    process serving multiple sites, or having multiple sites share a single
    database; however, this proposed compartmentalization should allow
    reduced risk when experimenting with new languages.

  - For now, all the code for all the dictionary applications will reside
    in this git repo, and not be split into separate git repos.

    That will make it much easier to move code around during development,
    and to run tests across all dictionary applications when making
    changes.

    Some day, we hope, when mature and stable, morphodict could go on PyPI
    as its own framework package with instructions on how to set up new
    languages without being in this git repo. We are very far from that
    point right now, but it’s something to keep in mind as a long-term
    goal.

[639-3]: https://iso639-3.sil.org/code_tables/639/data

## Layout

    $repo
    ├── .git/
    ├── package.json                # dependencies for bundlers, JS/CSS frameworks
    ├── Pipfile
    ├── arpeng-manage               # django-admin scripts are at the top-level for easy access
    ├── crkeng-manage
    ├── crkfra-manage
    ├── libexec/                    # programs only run by other programs
    ├── cwdeng-manage
    ├── srseng-manage
    ├── scripts/                    # various auxiliary scripts for devs / CI
    │   ├ reformat-altlabels
    │   └ …
    └── src/
        ├── morphodict/             # python package for language-independent code
        │   ├── __init__.py
        │   ├── analysis/           # package containing FST analysis code
        │   ├── api/                # back-end api endpoints, currently just for click_in_text
        │   ├── cvd/                # vector-based similarity (Cosine Vector Distance)
        │   ├── frontend/           # The existing front-end code moves here from src
        │   │   ├── dom-utils.js
        │   │   ├── index.js
        │   │   ├── orthography.js
        │   │   ├── …
        │   │   └── css/
        │   ⋮       ├── styles.css
        │           ├── variables.css
        │           └── …
        │   ├── lexicon/            # django app with primary database tables
        │   │   ├── __init__.py
        │   │   ├── models.py
        │   │   ├── management/
        │   │   │   └── commands/
        │   │   │       └── importjsondict.py
        │   │   ├── parser.py
        │   │   ├── test_parser.py  # test_* files are mixed in with non-test source code
        │   │   └── testdata/       # Use `testdata` directories for test data
        │   ├── orthography/        # Multi-orthography setup
        │   ├── paradigm/
        │   ├── phrase_translate/   # English Phrase Translation generalcode
        │   │   ├── sssttt/         # Source to Target (e.g. cwd -> eng) 
        │   │   └── tttsss/         # Target to Source (e.g. eng -> cwd)
        │   ├── preference/        
        │   ├── relabelling/        # Code for relabellings
        │   ├── search/             # Code for search        
        │   │   └── quality/        # Search quality code previously in search_quality
        │   ├── tests/              # Most of the tests.        
        │   └── utils/              # General-purpose utility code        
        │
        ├── crkeng/                 # python package for itwêwina
        │   ├── __init__.py
        │   ├── app/                # Django application (optional)
        │   │   ├── __init__.py
        │   │   ├── integration_tests/
        │   │   │   └── …           # tests that use resources/ of current language pair
        │   │   ├── templates/      # Django templates (overrides other apps)
        │   │   └── static/         # Static assets (Django staticfiles app)
        │   ├── cypress/
        │   │   └── …
        │   ├── docker/
        │   │   └── …
        │   ├── resources/          # Resources go here
        │   │   ├── altlabels.tsv
        │   │   ├── dictionaries/
        │   │   ├── fst/
        │   │   └── layouts/
        │   ├── site/               # Django project
        │   │   ├── __init__.py
        │   │   ├── settings.py
        │   │   ├── static/         # Logos and other static assets
        │   │   └── urls.py
        │   ├── frontend/           # Not a python package; language-specific frontend files
        │   │   ├── ….js
        │   │   └── css/
        │   │       └── ….css
        │   ├── generated/          # For files generated from other files; not checked in
        │   │   ├── collected_static/
        │   │   ├── built_js/
        │   │   ├── vector_models/
        │   │   └── …
        ├── cwdeng/                 # python package for Woods Cree dictionary
        │   ├── __init__.py
        │   ├── app/                # Django application (optional)
        │   │   ├── __init__.py
        │   │   ├── integration_tests/
        │   │   │   └── …           # tests that use resources/ of current language pair
        │   │   ├── templates/      # Django templates (overrides other apps)
        │   │   └── static/         # Static assets (Django staticfiles app)
        │   ├── cypress/
        │   │   └── …
        │   ├── docker/
        │   │   └── …
        │   ├── resources/
        │   │   ├── altlabels.tsv
        │   │   ├── dictionaries/
        │   │   ├── fst/
        │   │   └── layouts/
        │   ├── site/               # Django project
        │   │   ├── __init__.py
        │   │   ├── settings.py
        │   │   ├── static/         # Logos and other static assets
        │   │   └── urls.py
        │   ├── frontend/           # Not a python package; language-specific frontend files
        │   │   ├── ….js
        │   │   └── css/
        │   │       └── ….css
        │   └── generated/          # For files generated from other files; not checked in
        │       └── …
        ├── arpeng/
        ├── crkfra/
        ├── cr_shared               # for code and resources shared between Cree dialects
        └── srseng/

### Notes on source layout

  - The `sssttt` directories have parallel directory structures, containing
    a `site` python package for the django project, many python modules,
    but also directories for resources and frontend JS/CSS.

  - The hope for the top-level `src` directory containing python packages
    is that it makes it easier to run pytest/mypy/black across all our
    python code at once.

  - Python test files should be named `test_blah.py` and go in the same
    directory as the code they are testing. Do not create separate `test`
    directories. Tests are easier to find, update, and create when they are
    right next to the code they are testing, not in some other directory.

    There are arguments for and against both the `test_foo.py` and
    `foo_test.py` conventions; we [flipped a coin] and settled on
    `test_foo.py`.

  - That said, the cypress integration tests will live in their separate
    `cypress` folders. It is likely that there will be some shared tests in
    `morphodict/cypress` that will be used by every dictionary application,
    in addition to dictionary-specific tests.

  - We’re not specifying a new structure for the frontend JS/CSS code here.
    For now, we’ll keep doing whatever we’ve been doing, only the files
    will be stored in directories called `frontend` instead of `src`.

    We’ll start with everything in `src/morphodict/frontend` but
    language-specific JS/CSS will eventually go in `src/sssttt/frontend`.

[flipped a coin]: https://docs.python.org/3/library/random.html#random.choice

### Migration procedure

This proposal does not need to be adopted all at once or block other work.
Instead this proposal exists so that, when code must be moved in order to
accomplish higher-level goals such as making a dictionary work for a new
language, there are guidelines in place for where to move the code to. That
way itwêwina development doesn’t have to be blocked on moving everything
around, and development on new languages doesn’t have to be blocked as
often on figuring out where code should move to and what it should be
called.

This proposal is our best guess at how we can address some of the issues
we’ve run into in the past, and expect to run into in the future; if
something in here ends up not being workable, or causes more issues, then
by all means, update this plan.

The rough idea is:

  - A `crkeng` directory is created for itwêwina following the new structure.
    It imports all the code from `CreeDictionary`.  **Note: As of October 2024,**
    **the `CreeDictionary` package has been removed.**  It is referenced in
    this document for historical reasons.  We are keeping it around in this
    document until the internal package refactorings in `morphodict` reaches
    a stable state so that we can guarantee it is truly a language independent
    dictionary system.  

  - Work on itwêwina continues in the `CreeDictionary` package as normal,
    it’s just moved into the `src` directory, and gets run from
    `./crkeng-manage`

  - As we work to get parts of non-Plains Cree dictionaries working, we
    move code from `CreeDictionary` into either `morphodict` for
    language-independent stuff, or `sssttt` directories for things
    specific to certain language pairs.

    As pieces are moved out of `CreeDictionary`, pre-existing work on
    itwêwina will start to happen in `crkeng` and `morphodict` as well.

We can measure our progress somewhat by watching `CreeDictionary` shrink as
it moves into `crkeng` and `morphodict`.

PS:

  - In Python code, prefer absolute imports to relative ones for now, as
    they are more explicit, and will allow us to grep for `CreeDictionary`.
