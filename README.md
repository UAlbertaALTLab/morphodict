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
- Get Python 3.6 and [Pipenv](https://github.com/pypa/pipenv#installation).
- `$ pipenv install --dev`
- Install HFST

    Make sure `hfst-optimized-lookup` is a recognizable command on the terminal

    On Linux:

    > `$ sudo apt-get install -y hfst`

    On Mac:

    > Not tested. `$ brew install hfst`

    On Windows:

    > Not tested. Download hfstol binary file. Use `doskey` to alias as `hfst-optimized-lookup` if nessasary.

    For help, see [HFSTOL installation guide](https://github.com/hfst/hfst#installation-packages-for-debian-and-ubuntu)

- XML Dictionary Files

   Download `crkeng.xml` and `engcrk.xml` and place them under `CreeDictionary/res/dictionaries/`

   These files are copyright protected and not allowed on github. Ask coworkers or download from production server under the same directory. On server sapir, the direcotry is `/opt/cree-intelligent-dictionary/CreeDictionary/res/dictionaries/`

- Build Database

    - `$ manage-db import CreeDictionary/res/dictionaries/crkeng.xml` 
    
        It takes several minutes to process the xml file and write into the database. For better performance, enable multi-processing with `PROCESS_COUNT` being at most your cpu core count

        `manage-db import res/dictionaries/crkeng.xml --muti-processing PROCESS_COUNT` 
        
- Run development server
    - `pipenv run dev`
    - Default homepage: http://127.0.0.1:8000/cree-dictionary 
    - Default admin: http://127.0.0.1:8000/cree-dictionary/admin

## [Deployment](https://github.com/cmput401-winter2019/cree-intelligent-dictionary/wiki/Deployment)

## [Maintenance](https://github.com/cmput401-winter2019/cree-intelligent-dictionary/wiki/Maintenance)

## [Refactor Plan](https://github.com/cmput401-winter2019/cree-intelligent-dictionary/wiki/Refactor-Plan)

## [Project Structure](https://github.com/cmput401-winter2019/cree-intelligent-dictionary/wiki/Project-Structure)

## [Web API](https://github.com/cmput401-winter2019/cree-intelligent-dictionary/wiki/Web-API)

## License
This project licensed under Apache License Version 2.0
