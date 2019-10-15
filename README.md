# Cree Intelligent Dictionary

[![Build Status](https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary.svg?branch=master)](https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary)
[![codecov](https://codecov.io/gh/UAlbertaALTLab/cree-intelligent-dictionary/branch/master/graph/badge.svg)](https://codecov.io/gh/UAlbertaALTLab/cree-intelligent-dictionary)

## Project Description
A Cree/Syllabic to English and English to Cree/Syllabic dictionary,
that can define and return the linguistic analysis of each word.


## Production Website
http://sapir.artsrn.ualberta.ca/cree-dictionary

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

## Production on Sapir

### Redeployment Script

`.travis.yml` is configured so that after a successful build on master, sapir will execute a sequence of script to
update and restart the app. This is enabled by a tool`redeploy`, maintained by [Eddie](https://github.com/eddieantonio)

- The script does the following in sequence

   - pull the code
   - npm install
   - npm build (webpack js)
   - `pipenv install` to update dependencies
   - collect static
   - touch wsgi.py to restart service

- to change the script

    `vim scp://sapir.artsrn.ualberta.ca//opt/redeploy/redeploy/cree-dictionary`  (it's a python file without extension)

- to know details of how redeployment works, check the [repository of redeploy](https://github.com/eddieantonio/redeploy)

### Limit of `redeploy`

`redeploy` does not sync database file. After making changes to the database or the model file, we need to either
do migrations on Sapir or sync our database file, which is possible as sqlite database is operating system independent.

When you've made changes to the database, do `$ pipenv run push-db` to upload your database to Sapir

Just make sure your user is in `www-data` group on Sapir so that www-data on Sapir has access to the uploaded database.
If your username on Sapir is different from your username on you local machine. Add environment variable `SAPIR_USER=<your name>` in `.env` file.

### Set up

This only needs to be done once and is probably already done. This serves for documentation purpose.

- pull the code
- `sudo PIPENV_VENV_IN_PROJECT=1 pipenv install`

    This creates `.venv` folder under current directory. Without the environment variable pipenv will create virtual
    environment under the users home, which causes permission issues.

- `sudo pipenv run pip install mod_wsgi`

    DO NOT use `pipenv install`. mod_wsgi is used on sapir only to serve the application

- setup mod_wsgi

    ```.bash
    $ sudo pipenv run python CreeDictionary/manage.py runmodwsgi --setup-only --port=8091 --user www-data --group www-data --server-root=mod_wsgi-express-8091
    ```

    this creates folder `mod_wsgi-express-8091`, which contains a separate apache to serve the application.

- Create a service file `mod_wsgi-express-8091/cree-dictionary.service` with the following content

    ```
    [Unit]
    Description=Cree Dictionary HTTP service

    [Service]
    Type=forking
    EnvironmentFile=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/envvars
    PIDFile=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/httpd.pid
    ExecStart=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl start
    ExecReload=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl graceful
    ExecStop=/data/texts/opt/cree-intelligent-dictionary/mod_wsgi-express-8091/apachectl stop
    KillSignal=SIGCONT
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target
    ```

- `sudo pipenv run collect-static`

- `sudo systemctl enable $(realpath ./mod_wsgi-express-8091/cree-dictionary.service)`

- `sudo mkdir CreeDictionary/res/dictionaries`

- `cd .. && sudo chown -R www-data:www-data cree-intelligent-dictionary/`


- Have a `cree-dictionary.conf` with the following content under `etc/apache2/sites-available/`

    ```.conf
    # Add a trailing slash if it's missing.
    RedirectMatch 301 "^/cree-dictionary$"  "/cree-dictionary/"


    # A proxy for the cree-dictionary service, "sudo systemctl status cree-dictionary"
    ProxyPreserveHost On
    ProxyPass /cree-dictionary/ http://0.0.0.0:8091/cree-dictionary/
    ProxyPassReverse /cree-dictionary/ http://0.0.0.0:8091/cree-dictionary/
    ```

- `sudo a2ensite cree-dictionary`


## License
This project licensed under Apache License Version 2.0
