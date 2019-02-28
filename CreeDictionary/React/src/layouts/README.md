Paradigm layouts and metadata
=============================

Along with this README, you will find many TSV (tab-separated values)
files, and associated metadata files, stored in YAML format.

    .
    ├── na-basic.layout.tsv
    ├── na-basic.layout.yml
    ├── na-extended.layout.tsv
    ├── na-extended.layout.yml
    ├── na-full.layout.tsv
    ├── na-full.layout.yml
    ├── nad-basic.layout.tsv
    ├── nad-basic.layout.yml
    ├── nad-extended.layout.tsv
    ├── nad-extended.layout.yml
    ├── nad-full.layout.tsv
    ├── nad-full.layout.yml
    ├── ni-basic.layout.tsv
    ├── ni-basic.layout.yml
    ├── ni-extended.layout.tsv
    ├── ni-extended.layout.yml
    ├── ni-full.layout.tsv
    ├── ni-full.layout.yml
    ├── nid-basic.layout.tsv
    ├── nid-basic.layout.yml
    ├── nid-extended.layout.tsv
    ├── nid-extended.layout.yml
    ├── nid-full.layout.tsv
    ├── nid-full.layout.yml
    ├── vai-basic.layout.tsv
    ├── vai-basic.layout.yml
    ├── vai-extended.layout.tsv
    ├── vai-extended.layout.yml
    ├── vai-full.layout.tsv
    ├── vai-full.layout.yml
    ├── vii-basic.layout.tsv
    ├── vii-basic.layout.yml
    ├── vii-extended.layout.tsv
    ├── vii-extended.layout.yml
    ├── vii-full.layout.tsv
    ├── vii-full.layout.yml
    ├── vta-basic.layout.tsv
    ├── vta-basic.layout.yml
    ├── vta-extended.layout.tsv
    ├── vta-extended.layout.yml
    ├── vta-full.layout.tsv
    ├── vta-full.layout.yml
    ├── vti-basic.layout.tsv
    ├── vti-basic.layout.yml
    ├── vti-extended.layout.tsv
    ├── vti-extended.layout.yml
    ├── vti-full.layout.tsv
    └── vti-full.layout.yml

The file names are in this format:

    {lexeme class}-{name}.layout.{file type}

### Lexeme class

The part of speech this layout applies to. Note that you may assume that
only nouns and verbs inflect in Plains Cree; other words **do not
inflect**. The lemma class starts with either `n` or `v` for "noun" or
"verb", respectively. Then a subtype is provided (e.g., "nad" is noun,
animate, dependent; "vta" is **verb**, **transitive**, **animate**).

When a word form is analyzed, use its tags (e.g., `+V`, `+N`, `+TA`,
`+A`, `+D`, etc.) to match it to a layout.

### Name

This is a label for the layout. The current layouts are named in order
of detail, in ascending order of detail from "basic" to "extended" to
"full".

### File type

`.tsv` file is the layout as a tab-separated values file.

`.yml` is a YAML file containing metadata. For the moment, this metadata
can be ignored.


Layouts
-------

The layouts are stored in a tab-separated-values format, as exported by
Excel or LibreOffice.

Each cell in the TSV file is a cell in the displayed paradigm.

That is, the following TSV file defines a table that is 2 columns wide,
by 7 rows high (Note, tabs are visualized as a `␉` character, but are
a single U+0009 HORIZONTAL TABLATURE character):

    "1s poss (sg)"␉     =N+A+D+Px1Sg+Sg
    "2s poss (sg)"␉     =N+A+D+Px2Sg+Sg
    "3s poss (obv)"␉    =N+A+D+Px3Sg+Obv
    ␉                   : "Unspecified possessor"
    "X poss (sg)"␉      =N+A+D+PxX+Sg
    "X poss (pl)"␉      =N+A+D+PxX+Pl
    "X poss (obv)"␉     =N+A+D+PxX+Obv

Cell types
----------

Cells can either be **titles**, **word form templates**, or **empty**.

### Titles

Title cells are surrounded in double quotes, optionally preceded by
a `:` colon and whitespace, or followed by some whitespace and a colon.

For example:

 - `"1s poss (sg)"` is a title cell.
 - `: "Unspecified possessor"` is also a title cell.

It is recommended that title cells are converted into a `<th>` if
generating an HTML table.

If a colon is present, it signifies that the cell's contents should be
left-aligned or right-aligned, depending on where the colon is.

### Word form templates

Word form templates are requests to generate a word form from the FST.

| Pattern           | Special character   | Example                        | Example lookup string              |
|-------------------|---------------------|--------------------------------|------------------------------------|
| Exact match       | `=`                 | `=N+I+D+PxX+Sg`                | mitêh+N+I+D+PxX+Sg                 |
| Match anywhere    | (none)              | `Der/Dim+N+A+D+Px1Sg+Sg`       | nôhkomis+N+A+D+Px1Sg+Sg            |
| Star substitute   | `*`                 | `PV/e+*+V+TA+Cnj+Prs+1Sg+2SgO` | PV/e+wâpamêw+V+TA+Cnj+Prs+1Sg+2SgO |

The general steps are the same:

 1. Apply the lemma to the pattern to create the **lookup string**.
 2. Call `FST.generate()` on the lookup string.
 3. Generate one or more `<td>` cell containing a generated word form.

#### Match anywhere patterns

Concatenate the lemma to the tags with a `+` to create the lookup used
in `FST.generate()`. In concept, the match anywhere cells are supposed
to match that set of tags _anywhere_ in the analysis; in practice,
however, the match anywhere cells usually provide all of the tags to the
right of the lemma.

#### Exact match pattern

Remove the leading `=` from the tag, then concatenate the lemma to the
tags with a `+` to create the lookup used in `FST.generate()`.

#### Star substitute patterns

Substitute the star with the lemma to create the lookup used in
`FST.generate()`.

### Empty cells

Empty cells are those that either contain no content, or whose only
content is whitespace. When generating an HTML table, these empty cells
**MAY** be output as an empty `<td></td>` element. This allows the rest
of the table to maintain its spacing.
