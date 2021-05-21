# Dictionary DB Model

Model for aggregating Plains Cree dictionaries with norm matching. Currently a WIP

## Glossary

### Aggregate Entry

The basic unit of the aggregate dictionary containing data from both dictionaries, as well as the original data of the lemma, linguistic analysis, and similarity score.
#### Key Components
 - head
 - word class / POS
 - lemma
 - linguistic analysis
 - definition
 - stem
 - [similarity score](#similarity-score)
 - others
	 - morphemes
	 - semantic class
	 - corpus frequencies


### CW

The Cree Words Dictionary. One of the sources for aggregating.
#### Key Components
 - head
 - word class / POS
 - definition
 - stem
 - morphemes

### MD

The Maskwacis Cree Dictionary. One of the sources for aggregating.
#### Key Components
- head
- definition
- semantic class

NB: while MD does contain word classes, these are too broad for our purposes. Instead, word class will come from [CW](#cw)

### Norming

 For the purpose of this model, norming refers to limiting the differences between stylistic choices in the head and definition of dictionary sources for the purpose of matching.

#### Example

 - [CW](#cw): apihêw -- "s/he makes s.o. sit"
 - [MD](#md): apihew -- "He makes him sit."

- both are normed to: apihew -- "he makes him sit"

### Similarity Score

The numerical analysis of the similarity between two definitions. Currently a "Percent Match" method is used which ignores word repititions and most conjunctions.

#### Example

 - "a rock or stone" <> "rock, stone" --> 100% match

## Setup

You must have the following packages installed:

    fuzzywuzzy
    numpy
    pandas
    sqlite3

Reccomended

    python-Levenshtein


  The easiest way to install these packages is to run


    pip install [package name]

   in the terminal. If you have multiple versions of python, I reccomend using `pip3` in place of pip.

## Usage

To set up dictionary sources for comparison (i.e., perform norming), use

    python3 prep_sources.py PATH_TO_CW.CSV PATH_TO_MD.CSV PATH_TO_DDB

currently this takes as input the csv versions of the sources, but this can be changed in later developments.

To perform matching operations, use

    python3 compare_entries.py PATH_TO_DDB

## Interface

Currently there is no sophisticated custom interface for the DDB. However, while this is in the works I reccomend downloading and using [DB Browser For SQLite]([https://sqlitebrowser.org/](https://sqlitebrowser.org/)).
This software allows you to view, filter, sort, and modify the data without knowledge of SQL. There is also the option to execute SQL queries if you desire.

## Process Sketch

![process sketch](process%20sketch.png)
