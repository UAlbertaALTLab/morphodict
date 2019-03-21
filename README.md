# Cree Intelligent Dictionary

## Project Description
A Cree/Syllabic to English and English to Cree/Syllabic dictionary, 
that can define and return the linguistic analysis of each word.

Check wiki for detailed documentation.

## Run Development Server
> cd CreeDictionary\
> python manage.py runserver

## Install Dependencies
### Server
Python
> pip install requirements.txt\

React Requirements
> npm install\
> npm run dev

Other dependencies:
- Dictionary XML
- FST fomabin
- Imported SQLITE3 File

These must be obtained from other sources.

### Importer
Place hfst into the root directory.
 - Ex: cree-intelligent-dictionary\hfst

## Run Tests
### Django
> cd CreeDictionary\
> python manage.py test

### Front-end
> npm run e2e

### Importer
> cd DictionaryImporter
> ./RunTest.sh


## Project Structure
The project is broken into two parts:
- Django with React
- Dictionary Importer

Folder /CreeDictionary/ Contains:
- /CreeDictionary/API/
  - App for Server Back-end Code
- /CreeDictionary/React/ 
  - App for React Front-end Code and Resources
- /CreeDictionary/CreeDictionary/ 
  - Django Project Settings

Folder /DictionaryImporter/ Contains:
- /DictionaryImporter/DictionaryImporter.py
  - The Dictionary Importer. Run this to import using FST.
- /DictionaryImporter/DictionaryParser.py
  - The helper parser class for parsing XML and generation.
- /DictionaryImporter/test/
  - Tests for the classes
- /DictionaryImporter/RunTest.sh
  - Simple script to run all tests for DictionaryImporter

## License
This project licensed under Apache License Version 2.0