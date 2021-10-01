(dictionary_data)=

# Dictionary data

Dictionary applications require dictionary data.

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

### importjson formatting suggestions

To make it easier for humans to look at the raw dictionary data and to
compare different versions of that data, it is *extremely strongly
recommended* that you run

    ./sssttt-manage sortimportjson FILENAME

on any importjson files before committing or sharing them.

That automatically implements the following suggestions:

  - Run the importjson files through [`prettier`][prettier] to format them
    nicely. If using the command line, you’ll need to add a `--parser=json`
    argument as prettier does not automatically recognize the `.importjson`
    file extension.

  - Sort the entries by `slug`, with any `formOf` entries coming
    immediately after the corresponding lemma entry, and related `formOf`
    entries sorted together by `head`.

    Compare strings using [NFD unicode normalization][NFD] so that accented
    and non-accented characters sort near each other.

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
[NFD]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/normalize#canonical_equivalence_normalization
[json-stable-sort]: https://www.npmjs.com/package/json-stable-stringify

### importjson specification

An importjson file is a JSON file containing an array of entries.

There are two kinds of entries, normal entries and formOf entries.

#### Normal entries

The fields are:

  - The `head` field, a required string, is the head for the entry, in the
    internal orthography for the language. This is what is literally
    displayed in as the headword in the entry. It is usually a single
    wordform, but also could be a multiword phrase, non-independent
    morpheme, stem, &c.

  - The `senses` field, a required array of `{definition: string, sources:
    string[], coreDefinition?: string, semanticDefinition?: string}`
    objects, contains the definitions for the entry.

    Only the `definition` and `sources` fields are required.

    The `definition` must currently be an unformatted string. We are aware
    that people would like to specify things such as source-language text
    to be shown in the current orthography, cross-references, notes,
    examples, and so on, in a more structured manner.

    If we were starting from scratch we might call the `definition` field a
    `displayDefinition`, but we already have some data, and often it is the
    only one definition field provided.

    The `sources` are typically short abbreviations for the name of a
    source. `sources` is an array because multiple distinct sources may
    give the same, or essentially the same, definition for a word.

    The optional `coreDefinition` field may specify a definition to use for
    auto-translation. For example, if an entry for ‘shoe’ has lots of
    details and notes, but when auto-translated into first person
    possessive it should simply become ‘my shoe’, you can specify the core
    definition as `shoe`.

    The optional `semanticDefinition` field may specify a definition to use
    instead of the main definition text for the purposes of search. It will
    be used instead of the plain `definition` field for indexing keywords,
    and when computing definition vectors for semantic search. This is
    related to the concept of the core definition, but may add additional
    relevant keywords, while leaving out stopwords or explanatory text such
    as ‘see’ in ‘[see other-word]’ or the literal word ‘literally.’

  - The `slug` field, a required string, is a unique key for this entry
    that is used for several purposes, including user-facing URLs, to make
    `formOf` references, and for homograph disambiguation.

    Each normal entry must provide a `slug` that is distinct from every
    other normal entry. It is recommended that this field be the same as
    the `head`, including diacritics, but with any URL-unsafe characters
    stripped, and a homograph disambiguator added at the end if needed for
    uniqueness.

    How to create disambiguators is up to the lexicographer. For example,
    for the Plains Cree homograph `yôtin`, the lexicographer might set the
    slugs for the three entries to `yôtin@1` and `yôtin@2` and `yôtin@3`;
    or to `yôtin@na` and `yôtin@ni` and `yôtin@v`; or following any other
    scheme they desire, so long as the assignments remain relatively
    stable.

    Any homograph disambiguator should start with `@`, as there is code in
    morphodict to redirect an attempt to access an invalid homograph
    disambiguator like `/word/nîmiw@foo` into a search for `nîmiw`, whereas
    something like `nîmiw-foo` will do a search for `nîmiw-foo` instead of
    `nîmiw`. That way if disambiguators change due to adding and removing
    entries/definitions, old links should still be useful to people.

  - The `paradigm` field, an optional string, is the name of the paradigm
    used to display the paradigm tables for the entry. This may be a static
    or dynamic paradigm.

    This field may have a null value, or be omitted entirely, if the entry
    is indeclinable.

  - The `analysis` field, an optional array, is the analysis of the
    headword. This field is used to populate the linguistic breakdown popup
    shown by the blue ℹ️ icon.

    The required format is that of an entry from the list returned by
    `lookup_lemma_with_affixes`, e.g., `[[], "nîmiw", ["+V", "+AI", "+Ind",
    "+3Sg"]]`. The format is:

      - Array of:

          - Array of FST tag strings

          - FST lemma string

          - Array of FST tag strings

    This field may have a null value, or be omitted entirely, if the entry
    is unanalyzable.

  - The `linguistInfo` field, an optional arbitrary JSON object, allows
    extra presentation data to be stored in the database. Morphodict HTML
    templates have access to this data for the purpose of displaying
    additional data to the end user.

    Morphodict does not use any of this data for its core
    language-independent functionality.

    It is recommended *not* to put any unused data in here that ‘might be
    handy later,’ but only to add new things here when required as part of
    a coordinated effort with the frontend code to add new user-facing
    features.

  - The `fstLemma` field, an optional string, is the FST lemma to use when
    generating dynamic paradigm tables for unanalyzable forms in
    dictionaries that support that. It must not be specified when there is
    also an `analysis` field.

    To be clear on the concept that we’re talking about: the FST lemma is
    the thing that gets plugged into a paradigm layout template to generate
    associated wordforms. For example, if the head is `nîminâniwan` with
    FST analysis `nîmiw+V+AI+Ind+X`, then the FST lemma is `nîmiw`. If the
    head is `nimîw` with the FST analysis `nimîw+V+AI+Ind+3Sg`, then the
    FST lemma is `nimîw`, which is the same as the head.

    Normally the FST lemma is included as part of the `analysis`, and the
    code can retrieve the conceptual FST lemma from that `analysis`, so the
    separate `fstLemma` field is redundant and should not be explicitly
    included.

    However, sometimes it is desirable to have a dictionary entry that is
    not analyzable but for which dynamic paradigms should be displayed. For
    example, in Arapaho, one entry has the non-analyzable stem `níhooyóó-`
    as a head, which should display dynamic paradigms using the FST lemma
    `nihooyoo`. Therefore, that is precisely what the `fstLemma` field for
    this entry contains.

    In that case of dynamic paradigms for non-analyzable `head` entries,
    and only in that case, is this field useful.

    This field is only supported for languages with the
    `MORPHODICT_ENABLE_FST_LEMMA_SUPPORT` setting enabled, which is
    currently only Arapaho.

Note that the only strictly required fields are `head`, `slug`, and
`senses`. If no other fields are supplied, morphodict will still work, but
many interesting and useful features of morphodict will not; you will
essentially have a static dictionary application.

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

No other fields are valid on formOf entries.

#### Validation

The following importjson validation checks are intended to be implemented
for morphodict:

  - Every entry must have at least one non-empty definition, and every
    definition must have at least one valid source.

  - If an `analysis` is specified, it must be one of the results returned
    from doing an FST lookup on the `head`

  - If an `analysis` is specified, the `head` must be one of the results
    returned by running the `analysis` through the generator FST

  - `fstLemma` may not be specified if there is an `analysis`

  - The FST lemma in every `formOf` analysis must match the FST lemma of
    the corresponding normal entry

  - Strings must not begin with a combining character. If a string is
    intended to start with a diacritic, e.g., a floating tone such as
    `"´a"`, or `" ̣gwà…"`, use a non-combining character such as `´`, or if
    there is no non-combining equivalent such as for Combining Dot Below,
    put the combining character on a space, a non-breaking space, or a
    U+25CC ◌ Dotted Circle.

  - The `slug` must not contain certain URL-unsafe characters, e.g., `/`

#### Caveats

Known issues with the importjson format:

  - In many dictionaries, the order of definitions is very important, with
    the most common definitions being listed first. There is currently no
    code in morphodict to explicitly store or preserve the order of
    definitions. The dictionary is currently largely working by coincidence
    in that the import process and database tend to show the same results
    to the user as what was in the importjson file.

    This isn’t so much an issue with the input format, which does have an
    explicit definition order, as a warning that this order may not be
    preserved.

(where_dictionary_files_go)=
## Where do files go?

Each full dictionary for language pair [`sssttt`](sssttt) is intended to be
placed at

    src/${sssttt}/resources/dictionaries/${sssttt}_dictionary.importjson

There is a `.gitignore` rule to prevent accidentally committing them.

(building_test_dictionary_data)=
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

(current_dictionary_data)=
## Current dictionary data

In theory, linguists will provide comprehensive and correct dictionary data
in the morphodict-specific importjson format.

In practice, at this time, full dictionaries for each language arise as
follows:

  - For Plains Cree, there is `crk/dicts/crkeng_dictionary.importjson` checked
  in to the secret git repository at `altlab.dev:/data/altlab.git`. This is
  what’s used in production. It was created by importing the old `crkeng.xml`
  file into an older version of the software that did a lot of paradigm and
  analysis inference during import, and then the database contents were exported
  in the new importjson format.

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

## Cree `linguistInfo`

For the Plains Cree dictionary, the following `linguistInfo` fields are
used to display linguistic info in search results, and for showing emoji:

  - `inflectional_category`, String: The inflectional category for an
    entry, with hyphen, e.g., `NI-1`. (CW's `\ps`)

  - `pos`, String: The part of speech for this entry (`N` / `V` / `PRON`).
    If we were naming this today following our glossary, we would call it
    the *general word class*.

  - `stem`, String: The FST stem for this entry.

    For Plains Cree specifically, there are two variants of linguistic
    stems in the ALTLab crk-db. For both, a preceding hyphen (for dependent
    nouns, e.g. *-ohkom-*) and/or following hyphen (for all stems,
    e.g. *nimî-*) indicate that they can take additional prefixes/suffixes:

      - the minimal CW stem from `\stm` field in the CW toolbox source,
        which N.B. is lacking from MD and AECD. It should be present there
        for all words, but blank for non-independent morphemes, and might
        be a list when the head is a phrase. This minimal stem may lack
        lexicalized reduplicative elements and/or preverbs/prenouns, and
        thus may not have a one-to-one mapping to possible lemmas
        (e.g. *api-* as the minimal CW stem of the lemma *ay-apiw*.

      - the full FST stem according to the `fst.stem` field in the ALTLab
        crk-db. This includes all the reduplicative elements as well as
        preverbs/prenouns which have become lexicalized in a lemma, and
        thus has a one-to-one mapping with the lemma. This is created in
        the ALTLab crk-db based on the minimal stem, e.g. *ay-api-* as the
        full FST stem for the lemma *ay-apiw*. The FST stem, when
        supplemented with special morphophonological symbols, is used in
        the lexc source code for crk stems in the format: <`FST
        lemma`>:<`FST stem`>, e.g., [`acitakotêw:acitakot3 VTAt
        ;`][fst-stem1]

    itwêwina currently has the FST stem in the `linguistInfo.stem` field,
    and does not include a separate CW stem in the importjson. If display
    of the minimal CW stem were some day added to morphodict, that would of
    course require the dictionary data to include that data at that time.

  - `wordclass`, String: The word class for this entry (`VTA` / `VAI` / etc.).
    At one time our glossary called this a *specific word class*.

[FST-stem1]: https://github.com/giellalt/lang-crk/blob/8574d2b163d115e6da4419794f21ffe692d76b9b/src/fst/stems/verb_stems.lexc#L123
