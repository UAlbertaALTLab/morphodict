(dictionary_data)=

# Dictionary data

Dictionary applications require dictionary data.

## Abstract data

Having the following information available in some form is *extremely
useful* for developers, community members, and other linguists who are not
as familiar with the language, or your conventions for describing it, as
you are.

This may be in the form of prose documents, spreadsheets, diagrams, and so
on, as long as the intent is to provide reference material for humans to
understand what is going on.

  - **Part-of-speech categories** and the relations among them

    Linguists classify language elements into potentially overlapping
    categories with varying levels of detail, e.g., “nouns” and “verbs” and
    “type-1 animate intransitive verbs.” They also group these categories
    into other meta-categories, such as ‘part of speech’ or ‘word class’ or
    ‘linguistic category.’ For example, they may say that ‘nouns’ and
    ‘verbs’ are ‘parts of speech’ while ‘transitive verbs’ and
    ‘intransitive verbs’ are ‘word classes’ within the ‘verb’ ‘part of
    speech.’

    As handy as it would be, there is no universal terminology here, so
    please spell out what terminology you’re using!

    What categories do you have, what other categories do they contain or
    overlap with, and what if anything do you call the different
    meta-categories you use to group your categories?

The morphodict code only really cares about what it calls a ‘paradigm’: a
set of words where you’ll get a correct paradigm table output by using a
template with the same shape, the same labels, and the same FST tags but
differing entry-dependent FST lemmas for every word in the set.

So your transitive and intransitive verbs are likely to belong to different
paradigms from morphodict’s perspective because the respective generated
paradigm table outputs will have different shapes based on whether they
accommodate an object or not. But whether you have different
morphodict-paradigms within the intransitive verbs depends on both the
language and how the FST is implemented.

It’s extremely helpful to know how morphodict’s ‘paradigm’ concept maps to
the linguistic terminology for the language in question.

  - For each part-of-speech category:

      - What is the name of this category?

      - What abbreviations are typically used and/or preferred to refer to
        this category?

      - A prose description of the category.

      - What are some example members of this category?

      - Are the members declinable?

        If the members of this category are in theory declinable, but for
        practical purposes morphodict will not be doing any declining—maybe
        nobody’s figured out the rules yet, or the rules are known but
        nobody’s put them into an FST—it is useful to note that.

      - Do all the members of this category share the same paradigm table
        template, with the same FST tags but different FST lemma inputs?

        If the answer to this question is ‘no,’ morphodict cannot use this
        particular part-of-speech category as a paradigm, and you can skip
        the other questions for this category.

      - If the members of the category are declinable, then, for some
        example members, please provide one or more paradigm tables as
        might be found in instructional or reference material.

        These are extremely useful for checking that morphodict is
        displaying paradigms correctly correctly.

      - If the members are declinable, what is the preferred
        lemma/citation/infinitive form for a lexeme?

  - What additional information might people want to see as part of
    entries? Examples of the kinds of things that have been implemented or
    requested include showing stems, folio references to original linguist
    notebooks, proto-forms, and whether an entry is attested in a certain
    corpus.

(importjson-spec)=
## importjson

morphodict requires dictionary data to be supplied in a custom format
called `importjson`. It looks like this:

    [
      ⋮,
      {
        "analysis": [[], "nîmiw", ["+V", "+AI", "+Ind", "+3Sg"]],
        "head": "nîmiw",
        "linguistInfo": { "stem": "nîmi-" },
        "paradigm": "VAI",
        "senses": [{ "definition": "s/he dances", "sources": ["CW"] }],
        "slug": "nîmiw"
      },
      {
        "analysis": [[], "nîmiw", ["+V", "+AI", "+Ind", "+X"]],
        "formOf": "nîmiw",
        "head": "nîminâniwan",
        "senses": [
          {
            "definition": "it is a dance, a time of dancing",
            "sources": ["CW"]
          }
        ]
      },
      ⋮
    ]

This format is a subset of JSON that is intended to match the internal data
structures and terminology of morphodict code. It is not recommended as a
long-term storage format. It does not have room for everything a linguist
might want in a dictionary, only for the things that morphodict currently
supports. And it is unlikely to use your preferred linguistic terminology.

In practice you will want to store your canonical dictionary data in some
other format, such as [Daffodil], and write a short script to convert that
to importjson format.

[Daffodil]: https://format.digitallinguistics.io

**If you do not yet have all of the data available**—e.g., you may have a
draft dictionary that does not have paradigms or analyses assigned to
entries—it is still *hugely* beneficial if you can provide initial
dictionary data containing:

  - *All the definitions* you have available

  - At least one FST-analyzable entry *for every paradigm*

That is, when getting started, it’s better to have a full dictionary that
needs revision and is sparse on detail but provides full details for at
least one entry in every paradigm, than to have full details for more
entries but only from one or two paradigms. And it’s much better to have
some initial draft dictionary data covering the whole language, allowing
people to start working with it, than to have no data at all while waiting
for it to be ‘right.’

### importjson file suggestions

To make it easier for humans to look at the raw dictionary data and to
compare different versions of that data, the following points are *strongly
recommended*:

  - Run the importjson files through [`prettier`][prettier] to format them
    nicely. If using the command line, you’ll need to add a `--parser=json`
    argument as prettier does not automatically recognize the `.importjson`
    file extension.

  - Sort the entries by slug, with any `formOf` entries coming immediately
    after the corresponding lemma entry, and related `formOf` entries
    sorted together by `head`.

    Compare strings using NFD unicode normalization so that accented and
    non-accented characters sort near each other.

  - Explicitly sort the *keys* of the emitted JSON objects. Otherwise the
    JSON object keys can be emitted in random or insertion order, creating
    unnecessary noise in diff output. In JS you can try the
    [json-stable-sort] package, and in Python the `json.dump` functions
    take an optional `sort_keys=True` argument.

  - Make sure that the JSON you are emitting has unicode strings instead of
    asciified strings with human-unfriendly escape sequences. For example,
    in python, the `json.dump()` function needs an extra
    `ensure_ascii=False` keyword argument or you will get
    `"w\\u00e2pam\\u00eaw"` instead of `"wâpamêw"`.

[prettier]: https://www.npmjs.com/package/prettier
[json-stable-sort]: https://www.npmjs.com/package/json-stable-stringify

### importjson Specification

An importjson file is a JSON file containing an array of entries.

There are two kinds of entries, normal entries and formOf entries.

#### Normal entries

Property                             | Type             | Description
-------------------------------------|------------------|-----------------
`analysis`                           | Array            | The rich analysis returned from the FST (`lookup_lemma_with_affixes`; an array of features and the lemma for the entry).
`formOf`                             | String           | A cross-reference to the entry that this entry is a form of. This is used especially when the current entry is an inflected form of a lexeme. The value of this field should be the slug (unique key) of the cross-referenced entry.
`fstLemma`                           | String           | The FST lemma for this entry. This is only used for entries where a) the headword is not analyzable, but b) we still want to generate a paradigm table.
`head`                               | Object           | The head(word/phrase/morpheme) for the entry, in the internal orthography for the language. This is what is literally displayed in as the headword in the entry. Currently there is no distinction made in the app between head and lemma, so the data in this field is actually the linguistic lemma, stripped of any punctuation.
`paradigm`                           | String or `null` | The paradigm layout that should be displayed for this entry. `null` if no paradigm should be displayed.
`senses`                             | Array<Object>    | The definitions for this entry.
`sense.definition`                   | String           | The definition for this sense.
`sense.sources`                      | Array<String>    | The sources for this definition.
`slug`                               | String           | The slug to display in the URL for this entry. Also functions as the unique key for this entry.
`linguistInfo`                       | Object           | Data used in the app for display purposes only.
`linguistInfo.analysis`              | String           | The FST analysis of this entry.
`linguistInfo.head.proto`            | String           | The headword in the proto-orthography.
`linguistInfo.head.sro`              | String           | The headword in SRO.
`linguistInfo.inflectional_category` | String           | The inflectional category for an entry, with trailing hyphen. (CW's `\ps`)
`linguistInfo.pos`                   | String           | The part of speech for this entry. (`N` / `V` / `PRON`)
`linguistInfo.stem`                  | Object           | The linguistic stem for this entry.
`linguistInfo.stem.proto`            | String           | The linguistic stem for this entry, in the proto-orthography.
`linguistInfo.stem.sro`              | String           | The linguistic stem for this entry, in SRO.
`linguistInfo.wordclass`             | String           | The word class for this entry. (`VTA` / `VAI` / etc.)



#### formOf entries

These entries add additional definitions to inflected forms of normal
entries.

In the morphodict application, formOf entries are described as being a
‘form of’ the corresponding normal entry.

Some linguists feel that, lexicographically, these entries may be more
appropriate as standalone normal entries, on the grounds that having a
distinct definition implies being a distinct lexeme. Others argue that
there is room for certain inflected forms to have their own connotations
and shades of meaning, even in English, but especially in morphologically
complex languages.

The fields are:

  - The `formOf` field, a string, must equal the `slug` of a normal entry
    in the same importjson file.

  - The `head` field has the same format and meaning as for normal
    entries.

  - The `senses` field has the same format and meaning as for normal
    entries.

  - The `analysis` field has the same format and meaning as for normal
    entries, but with the additional condition that the formOf `analysis`
    FST lemma must equal the FST lemma of the corresponding normal entry.

No other fields are permitted on formOf entries.

(where_dictionary_files_go)=
## Where do files go?

Each full dictionary is intended to be placed at

    src/${sssttt}/resources/dictionaries/${sssttt}_dictionary.importjson

There is a `.gitignore` rule to prevent accidentally committing them.

### Building test dictionary data

Test dictionaries are created by taking subsets of the full dictionaries,
and storing them beside the full dictionaries as
`${sssttt}_test_db.importjson`.

*These files are checked in so that people can do development and testing
without having any access to the full dictionary files which have
restricted distribution.*

To update them, you’ll need a copy of the full dictionary file.

 1. Edit `src/${sssttt}/resources/dictionary/test_db_words.txt`

 2. Run `./${sssttt}-manage buildtestimportjson` to extract the words
    mentioned in `test_db_words.txt`, from
    `${sssttt}_dictionary.importjson` into `${sssttt}_test_db.importjson`

 3. Commit your changes and send a PR.

*Exception: the current crkeng test database omits many unused keys,
e.g., `wordclass_emoji`, that currently exist in the production
`crkeng_dictionary.importjson` file.*


## Current dictionary data

In theory, linguists will provide comprehensive and correct dictionary data
in the morphodict-specific importjson format.

In practice, at this time, full dictionaries for each language arise as
follows:

  - For Plains Cree, there is `crk/dicts/crkeng_dictionary.importjson`
    checked in to the secret git repository at
    `altlab.dev:/data/altlab.git`. This is what’s used in production. It
    was created by importing the old `crkeng.xml` file into an older
    version of cree-intelligent-dictionary that did a lot of paradigm and
    analysis inference during import, and then the database contents were
    exported in the new importjson format.

  - For Woods Cree, the `munge/cwdeng/cwdize` script transliterates the
    production `crkeng_dictionary.importjson` file, using the
    `database.ndjson` file from the ALTLab repo to get the proto-Cree
    forms.

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

### Building

To install the prerequisites of the munge scripts:

    cd munge
    npm install

Then, running them takes a little bit of fiddling because they are written
in TypeScript and need to be transpiled to JavaScript. To do that on the
fly:

    node -r sucrase/register/ts cwdeng/cwdize.ts --help

In several of the directories there is an executable `run.js` script to do
that for you, so it could be as simple as `./run.js --help`.


## Dictionary entry level

For each dictionary entry, we will need the following pieces of data:

  - The entry head. In most dictionaries this is usually a single word, but
    could also be a phrase or morpheme.

  - The inflectional category. Plains Cree can use inflectional categories
    such as `IPH` “indeclinable phrase” and `IPM` “indeclinable morpheme”
    for non-word heads.

  - The FST lemma. This is specified iff the inflectional class is
    declinable. To be clear: the FST lemma is the thing that gets plugged
    into a paradigm layout template to generate associated wordforms. For
    example, if the head is `kinîminâwâw` with FST analysis
    `nîmiw+V+AI+Ind+2Pl`, then the FST lemma is `nîmiw`.

  - A list of definitions for the head. Each definition is typically a
    string, and a list of citation abbreviations. There is intent to enrich
    this data model by specifying things such as cross-references, notes,
    and examples; specifying that is not in this document’s scope at the
    moment.

  - The homograph key. In order to have stable ways to refer to different
    homographs in the database and in URLs, whenever two or more heads have
    the same text, each entry with a head that is a homograph must provide
    a homograph key that is distinct from every other wordform.

    For example, for the Plains Cree homograph `yôtin`, the lexicographer
    might set the keys for three wordforms to `yôtin1` and `yôtin2` and
    `yôtin3`; or to `yôtin-na` and `yôtin-ni` and `yôtin-v`; or following
    any other scheme they desire, so long as the assignments will remain
    stable.

    For convenience when the dictionary source has its own stable
    identifiers, the homograph key may be set on every dictionary entry,
    and will only be used on entries that are actually homographs.

    Note that homographs may or may not be in the same inflectional
    category.

  - Optionally, a static paradigm name. Specifying this is only permitted
    if the specific word class should not be declinable. For example, in
    Plains Cree, ‘niya’ from the indeclinable inflectional category `PrA`
    “animate pronouns” has static paradigm `personal-pronouns`.

  - Optionally, the linguistic stem. This is displayed on the website for
    humans to see, but is not accessed or used for any other purposes by
    the dictionary code. This is technically optional because not all
    dictionary sources and language pairs will have this information and/or
    want to display it.

    For Plains Cree specifically: This is the `\stm` field in the *Cree:
    Words* toolbox file and the value ends with a `-`, e.g., `nîmi-`. It
    should be present there for all words, but absent for morphemes, and
    might be a list when the head is a phrase. After appropriate processing
    such as removing the trailing hyphen and ensuring preverbs and
    reduplication are included and remapping some symbols, it becomes the
    “FST stem” in the lexc source code as `<FST lemma>:<FST stem>`, e.g.,
    [`acitakotêw:acitakot3 VTAt
    ;`](https://github.com/giellalt/lang-crk/blob/8574d2b163d115e6da4419794f21ffe692d76b9b/src/fst/stems/verb_stems.lexc#L123)
