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
> python manage.py test API

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

## Web API
### Search
**/Search/\{QueryString\}**

The parameter query string can be anything such as:
- English word
- Cree word
- Cree Inflection
- Cree Incomplete Inflection
- Misspelled Cree Words

A JSON Object will be returned. The structure is:

- "words" property has an array of lemma objects
  - "id" Lemma unique id
  - "context" The lemma itself
  - "type" Type of the lemma, can be N, V, IPV or Empty
  - "language" Language of the lemma (crk = Cree, eng = English)
  - "word_ptr" Word unique id
  - "attributes" An array of attibute objects
    - "id" Attribute ID
    - "name" Attribute Name (Ex: "N" or "A" or "D" for a NAD word)
    - "fk_lemma" Lemma Unique ID
  - "definitions" An array of definition objects
    - "id" Definition ID
    - "context" The definition itself
    - "source" Dictionary Source
    - "fk_word" Word Unique ID


### DisplayWord
**/DisplayWord/\{Lemma\}**

The parameter Lemma must be in its exact SRO form.

A JSON Object will be returned. The structure is:

- "lemma" property is a lemma object (Same structure as above)
- "inflections" properties is an array of inflection objects
  - "id" Inflection unique id
  - "context" The inflection itself
  - "type" Type of the inflection, can be N, V, IPV or Empty
  - "language" Language of the inflection (crk = Cree, eng = English)
  - "word_ptr" Word unique id
  - "inflectionForms" An array of inflection form objects
    - "name" Inflection Form Name (Ex: "V" or "TA" or "Ind" for a {lemma}+V+TA+Ind inflection)
  - "definitions" An array of definition objects **(Optional)**
    - "id" Definition ID
    - "context" The definition itself
    - "source" Dictionary Source
    - "fk_word" Word Unique ID


## License
This project licensed under Apache License Version 2.0