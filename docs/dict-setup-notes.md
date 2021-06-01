# Rough guide to setting up non-intelligent dictionaries

Rough outline:

  - There is a `${sss}import` command to convert something to xml
  - Then run `xmlimport ${sssttt}.xml`

## cwdeng

    ./cwdeng-manage cwdimport $SECRET_ALTLAB_REPO/cwd/dicts/llr/llr.json
    ./cwdeng-manage xmlimport cwdeng.xml

## arpeng

    ./arpeng-manage arpimport $ARAPAHO_LINGUISTIC_DATA_REPO/arapaho_lexicon.json
    ./arpeng-manage xmlimport arpeng.xml

## srseng

First, in the gunaha repo:

  - copy
    `$SECRET_ALTLAB_REPO/srs/dicts/Onespot-Sapir-Vocabulary-list-OS-Vocabulary.tsv`
    to `run/private/Onespot-Sapir-Vocabulary-list-OS-Vocabulary.tsv`.

  - run `poetry run ./manage.py importdictionary --json-only`
  - That produces the file `Onespot-Sapir.json`

Then, in *this* repo:

    ./srseng-manage srsimport $GUNAHA_REPO/Onespot-Sapir.json
    ./srseng-manage xmlimport srseng.xml

