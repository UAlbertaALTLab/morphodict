(dictionary_data)=

# Dictionary data

Dictionary applications require dictionary data.

## Sources

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

## Building

To install the prerequisites of the munge scripts:

    cd munge
    npm install

Then, running them takes a little bit of fiddling because they are written
in TypeScript and need to be transpiled to JavaScript. To do that on the
fly:

    node -r sucrase/register/ts cwdeng/cwdize.ts --help

In several of the directories there is an executable `run.js` script to do
that for you, so it could be as simple as `./run.js --help`.

## Where do files go?

Each dictionary is intended to be placed at

    src/${sssttt}/resources/dictionaries/${sssttt}_dictionary.importjson

There is a `.gitignore` rule to prevent accidentally committing them.

## Building test dictionary data

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

# Data format info

The data which is needed for setting up a dictionary application is as
follows. Note that this is an abstract description of what’s needed,
separate from details of field names or data formats like JSON or XML.

## Language level

Some thing are needed to describe the language itself, before dealing with
any one particular dictionary entry.

  - For each inflectional category:

    - The category name, e.g., `VAI-1`

    - A prose description spelling out any abbreviations in the name,
      e.g., “type-1 animate intransitive verbs.” This is used only by
      developers / linguists, and not shown to dictionary end-users.

    - The specific word class that the inflectional category belongs to

  - For each specific word class:
      - The specific word class name, e.g., `VAI`
      - A prose description
      - The general word class that the specific word class belongs to,
        e.g., `V`

      - The paradigm layout list. This will be used for generating
        wordforms. An example entry could be, `${lemma}+N+A+D+PxX+Sg`.

        *Instead of directly specifying a list of expansions, we only
        support automatically extracting this list from paradigm layout
        files.* This prevents data redundancy and inconsistency.

        In practice, this list may be empty even if the specific word class
        should be declinable; see the next bullet point.

      - Whether the specific word class *should* be declinable. Some word
        classes are indeclinable because that’s how the language works.
        Other word classes, although they should be declinable, won’t
        actually be declinable in practice by this application for reasons
        such as:
          - The paradigm layout files haven’t been written
          - There is no FST yet, or it doesn’t yet handle this specific
            word class
          - The dictionary entries haven’t been tagged with enough
            specificity to identify the paradigm

  - For each general word class:
      - The general word class name, e.g., `V`
      - A prose description

Note that it may be useful to have inflectional categories and general and
specific word classes for ‘unknown’; both generically, and for more refined
concepts such as ‘verb with unknown inflectional category.’ This helps to
keep separate the two distinct concepts of (1) word classes whose members
are not declinable because that’s how the language works, and (2) word
classes that should be declinable but where the required linguistic data
together with a compatible computational model implementation is not
presently at hand.

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
