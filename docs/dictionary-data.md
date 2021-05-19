The data which is needed for setting up a dictionary application is as
follows.

This is an abstract description of what’s needed, separate from details of
field names or data formats like JSON or XML.

## Language level

There are some things we need to describe the language itself, before we
look at any one particular dictionary entry.

  - For each inflectional category:
    - The category name, e.g., `VAI-1`
    - A textual description spelling out any abbreviations in the name,
      e.g., “type-1 animate intransitive verbs”
    - The specific word class that this inflectional category belongs to

  - For each specific word class:
      - The specific word class name, e.g., `VAI`
      - The general word class that the specific word class belongs to,
        e.g., `V`
      - Whether the specific word class *should* be declinable. Some word
        classes are indeclinable because that’s how the language works.
        Other word classes should be declinable, but won’t actually be
        declinable in practice by this application for reasons such as:
          - The paradigm layout files haven’t been written
          - The FST hasn’t been implemented yet for this specific word
            class
          - The dictionary entries haven’t been tagged with enough
            specificity to identify the paradigm

        the following info is also needed, but happily comes from the paradigm
        layout files right now:

        paradigm layout list used for generating wordforms
            note: may be empty because indeclinable,
            or because we just haven’t created a paradigm and/or FST that can
            handle it

Note that we will sometimes have inflectional categories for `?` = ‘unknown’
 or `V?` = ‘verb with unknown inflectional category’


dictionary level:

    for each dictionary entry: 
    - head (could be word, phrase, or morpheme)
    - inflectional category
      IPH indeclinable phrase / IPM indeclinable morpheme
    - FST lemma, if inflectional class is declinable
      To be clear: if the head is `kinîminâwâw` with analysis
      `nîmiw+V+AI+Ind+2Pl`, then the FST lemma is `nîmiw`
    - list of definitions

    - linguistic stem to display on popup

      (always in Arok’s source except for moprhemes; might be list for phrase)
      Arok’s \stm fields may not have preverbs or reduplication

      relation to FST is, Arok’s stems are used to create the FST lemmas
      in the lexc

      lexc source code has `<FST lemma>:<enriched FST stem, without trailing -, and maybe with alternate symbols like n2 or n3>`

      e.g., `acitakotêw:acitakot3 VTAt ;`

    https://github.com/giellalt/lang-crk/blob/main/src/fst/stems/verb_stems.lexc#L111-L141



    - homograph key
      note that homographs may be in the same inflectional category, may not be

    - static paradigm, only allowed if specific word class is indeclinable
      e.g., ‘niya’ has paradigm ‘personal pronoun’

