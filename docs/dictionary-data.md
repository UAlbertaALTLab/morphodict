## Current dictionary data

In theory, linguists will provide comprehensive and correct dictionary data
in importjtson format.

In practice, at this time, full dictionaries for each language arise as
follows:

  - For Plains Cree, there is `crk/dicts/crkeng_dictionary.importjson`
    checked in to the secret git repository at
    `altlab.dev:/data/altlab.git`. This is what’s used in production. It
    was created by importing the old `crkeng.xml` file into an older
    version of cree-intelligent-dictionary, that did a lot of paradigm and
    analysis inference during import, and then the database contents were
    exported in the new importjson format.

  - For Woods Cree, the `cwdize` script transliterates the production
    `crkeng_dictionary.importjson` file, using the `database.ndjson` file
    from the ALTLab repo to get the proto-Cre forms.

  - For Arapaho, the [private arp-db
    repo](https://github.com/UAlbertaALTLab/arp-db) has
    `arapaho_lexicon.json`, and the `munge/arpeng/toimportjson.ts`
    script transforms that to importjson.

  - For Tsuut’ina, there’s a deprecated spreadsheet on Google Drive. Get
    the link from `srs/README.md` in the ALTLab repo, as I’m not sure it’s
    intended to be public.

    Download the single-tab spreadsheet as a .tsv file, and
    `munge/srseng/toimportjson.ts` will transform that to importjson.

None of these are publicly available as the creators of the source content
have not given permission to make them publicly available in that form. For
Arapaho we believe we could make the data public, but have not yet had
sufficiently official confirmation of that.

Each of these dictionaries is intended to be placed at

    src/${sssttt}/resources/dictionaries/${sssttt}_dictionary.importjson

There is a `.gitignore` rule to prevent accidentally committing them.

### Building test dictionary data

Test dictionaries are exclusively created by taking subsets of the full
dictionaries.

*These files are checked in so that people can do development and testing
without having any access to the full dictionary files which have
restricted distribution.*

To update them:

 1. Edit `src/${sssttt}/resources/dictionary/test_db_words.txt`

 2. Run `./${sssttt}-manage buildtestimportjson` to extract the words
    mentioned in `test_db_words.txt`, from
    `${sssttt}_dictionary.importjson` into `${sssttt}_test_db.importjson`

 3. Commit your changes and send a PR.

*Exception: the current crkeng test database omits many unused keys,
e.g., `wordclass_emoji`, that currently exist in the production
`crkeng_dictionary.importjson` file.*
