## Development

- `$ git clone https://github.com/UAlbertaALTLab/cree-intelligent-dictionary.git`
- `$ cd cree-intelligent-dictionary`
- Get Python 3.6 and [Pipenv](https://github.com/pypa/pipenv#installation).
- `$ pipenv install --dev`
- Install HFST

    Make sure `hfst-optimized-lookup` is a recognizable command on the terminal

    On Linux:

    > `$ sudo apt-get install -y hfst`

    On Mac:

    > `$ brew install UAlbertaALTLab/hfst/hfst`

    On Windows:

    > Download hfstol binary file. Add bin folder to system path.

    For help, see [HFSTOL installation guide](https://github.com/hfst/hfst#installation-packages-for-debian-and-ubuntu)

- XML Dictionary Files

   Download `crkeng.xml` and `engcrk.xml` and place them under `CreeDictionary/res/dictionaries/`

   These files are copyright protected and not allowed on github. Ask coworkers or download from production server under the same directory. On server sapir, the direcotry is `/opt/cree-intelligent-dictionary/CreeDictionary/res/dictionaries/`

- create a file named `.env` under project root with `DEBUG=true`. (used both by npm and pipenv)

- `pipenv shell`

- Initialize Database

    `pipenv run make-migrations && pipenv run migrate`

- Build Database

    `$ manage-db import CreeDictionary/res/dictionaries/`

    It takes several minutes to process the xml file and write into the database. For better performance, enable multi-processing with `PROCESS_COUNT` being at most your cpu core count

    `$ manage-db import CreeDictionary/res/dictionaries/ --muti-processing PROCESS_COUNT`

    optionally `python ./CreeDictionary/manage.py createsuperuser` to use django admin

- Run development server
    - `npm run start`
    - index: http://127.0.0.1:8000/
    - admin: http://127.0.0.1:8000/admin

## Unit Tests

`pipenv run test`

It recognizes the following:

- The Django settings module in `setup.cfg` (for `pytest-django` to work)
- `--doctest-modules` `--mypy` in `Pipfile [script]` (to enable doctest and Mypy tests)
- `DEBUG=False` in `.env`

## Cypress integration tests

`npm test`

It also takes in variables from `.env` file

## Profiling Code

`pipenv run profile <script_name>`

with `<script_name>` being one of the scripts from `profiling` folder

e.g.

`pipenv run profile word_search[.py]`

You can come up with profiling scripts yourself

## Format Python code

We format all Python code with [Black](https://black.readthedocs.io/en/stable/)

To run it on all of the files:

    pipenv run format

> **Protip**! Make this a part of your git pre-commit hook!


