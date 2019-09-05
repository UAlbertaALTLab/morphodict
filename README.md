# Cree Intelligent Dictionary

[![Build Status](https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary.svg?branch=master)](https://travis-ci.org/UAlbertaALTLab/cree-intelligent-dictionary)

## Project Description
A Cree/Syllabic to English and English to Cree/Syllabic dictionary, 
that can define and return the linguistic analysis of each word.


## Production Website
http://sapir.artsrn.ualberta.ca/cree-dictionary

## Development

- `$ git clone https://github.com/UAlbertaALTLab/cree-intelligent-dictionary.git`
- `$ cd cree-intelligent-dictionary`
- Get Python 3.6+ and [Pipenv](https://github.com/pypa/pipenv#installation).
- `$ pipenv install --dev` or `$ pipenv install --dev --skip-lock` on Windows for [a behaviour of pipenv](https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/blob/feat/DictionaryImporter/README.md#known-issues).
- Install HFST

    Make sure `hfst-optimized-lookup` is a recognizable command on the terminal

    On Linux:

    > `$ sudo apt-get install -y hfst`

    On Mac:

    > Not tested. `$ brew install hfst`

    On Windows:

    > Download hfstol binary file. Add bin folder to system path.

    For help, see [HFSTOL installation guide](https://github.com/hfst/hfst#installation-packages-for-debian-and-ubuntu)

- XML Dictionary Files

   Download `crkeng.xml` and `engcrk.xml` and place them under `CreeDictionary/res/dictionaries/`

   These files are copyright protected and not allowed on github. Ask coworkers or download from production server under the same directory. On server sapir, the direcotry is `/opt/cree-intelligent-dictionary/CreeDictionary/res/dictionaries/`

- creat a file named `.env` under project root with `Production=False` on first line.

- `pipenv shell`

- Initialize Database

    `pipenv run make-migrations && pipenv run migrate`

- Build Database

    `$ manage-db import CreeDictionary/res/dictionaries/crkeng.xml` 
    
    It takes several minutes to process the xml file and write into the database. For better performance, enable multi-processing with `PROCESS_COUNT` being at most your cpu core count

    `$ manage-db import CreeDictionary/res/dictionaries/crkeng.xml --muti-processing PROCESS_COUNT` 

    optionally `python ./CreeDictionary/manage.py createsuperuser` to use django admin  

- Run development server
    - `pipenv run dev`
    - Default homepage: http://127.0.0.1:8000/cree-dictionary 
    - Default admin: http://127.0.0.1:8000/cree-dictionary/admin
    
    note the **cree-dictionary/** part

## Run Tests

`pipenv run test` 

It recognizes the following:

- django settings in pytest.ini (for `pytest-django` to work)
- --doctest-modules --mypy in `Pipfile [script]` (to enable doctest and mypy tests)
- Production=False in `.env`


## License
This project licensed under Apache License Version 2.0

## Known issues

### Pipenv install on Windows
On Windows, pipenv locking doesn't respect os_name marker and will error.

If you are doing development on windows. do `pipenv install --dev --skip-lock`

```pipfile
# mod-wsgi is a dependency in Pipfile
mod-wsgi = {version="~=4.6", os_name = "=='posix'"}
```
See the [pipenv issue](https://github.com/pypa/pipenv/issues/3929#issue-488682330) here
