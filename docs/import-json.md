(importjson-spec)=

# Import JSON Specification

Documentation of the JSON format for importing data into the intelligent dictionary app.

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
