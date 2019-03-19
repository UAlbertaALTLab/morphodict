# Cree Intelligent Dictionary

## Project Description
A Cree/Syllabic to English and English to Cree/Syllabic dictionary, 
that can define and return the linguistic analysis of each word.

Check wiki for detailed documentation.

## Install Dependencies
Python
> pip install requirements.txt

React Requirements
> ...

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