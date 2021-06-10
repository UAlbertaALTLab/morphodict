Paradigm layouts
================

This document describes `morphodict`'s **paradigm layout** package.

In the context of this document, a _paradigm_ is a table of related
wordforms. The exact nature of how the wordforms are related to one
another is not specified here — rather, that is for language experts to
specify.

The paradigm layout package is intended to work in conjunction with an
**analysis** and **generation** system, such as a **finite-state
transducer** (FST) for inflection. This enables **dynamic paradigm
layouts** (layouts with placeholders) to be used for a large number of
lexemes with the same _linguistic paradigm_.

Paradigm layout files
---------------------

**Paradigm layouts files** describe how to arrange wordforms in a table
format.

Layouts are tab-separated values (TSV) files, where each cell specifies
its role in the presented paradigm. The TSV file **must** be in the
**UTF-8** character encoding scheme.

Paradigm layouts are:

 - a series of **panes** — a sub-table of related wordforms
 - each pane consists of a series of **rows**, which is either
   a **header** or a **content** row
 - each **content row** consists of a series of **cells**
 - a cell can either be a **row label**, a **column label**, or
   a **wordform cell**.

### Syntax

Cells are separated by one U+0009 CHARACTER TABULATION character
(horizontal tab character).

Each row in the TSV file _should_ contain the same number of tab
characters. This is to facilitate display and editing of the TSV files
in tools that expect an equal amount of tabs per row (e.g., the GitHub
previewer, [VisiData][vd], common spreadsheet software,
[PyCharm][pycharm-tsv]).

Each panes is separated by one "blank" lines. A "blank" means any line
that only consists of whitespace (including the tab character).

A row can either be a:

 - **content row**: a row with **cells**
 - **header row**: its first cell must be a **header label**, followed
   by whitespace.

A **label** is a single cell with one or more FST-style tags. Each tag
in the label begins with a **prefix**, a **space character**, and then
the tag proper. Each tag within a label is separated by a single space.

These are the different prefixes:

 - `#`: header labels: describes an entire pane
 - `_`: row labels: describes the row in the current pane
 - `|`: column labels: describes the column in the current pane

For example, `# Past # Indicative` is a **header** label that has two
**tags**: `Past` and `Indicative`. A separate **relabelling** system is
intended to interpret the tags to display a user-facing string.

A cell can be a **label** (as described above), **empty** (consisting
of zero or more whitespace characters, a **missing** cell, consisting
exactly of the string `--` or a **wordform** cell.

A wordform cell **may** contain a `${lemma}` placeholder. In which case,
the paradigm layout is a dynamic layout, and the layout cells must be
_filled_ before the layout is ready for presentation. Regardless if the
wordform cell contains a `${lemma}` placeholder, there are few
limitations in what can go in a wordform cell. As of now,
a wordform cell is assumed to consist of either the literal wordform's
text or an _FST analysis_ string.

### Example

Here is a paradigm layout file with two **panes**, each with
a **header**, and each row with row labels and each column with column
labels:

Source: <https://docs.google.com/document/d/1nWQQvHgjGnXzOswm_TsnLx75Yp0-qzamTSm-7_INEsw/edit#>


### Partial Grammar


### Example



[vd]: https://www.visidata.org/
[pycharm-tsv]: https://www.jetbrains.com/help/pycharm/editing-csv-and-tsv-files.html


Where to place paradigm layout files
------------------------------------

Paradigm layout files are placed in the following directory structure
template:

```
layouts
├── dynamic
│   ├── {paradigm-name}
│   │   ├── {size-1}.tsv
│   │   ├── {size-2}.tsv
│   │   └── {size-3}.tsv
│   ├── {paradigm-name}
│   └── {paradigm-name}
└── static
    ├── {paradigm-name}
    │   ├── {size-1}.tsv
    │   ├── {size-2}.tsv
    │   └── {size-3}.tsv
    ├── {paradigm-name}.tsv
    └── {paradigm-name}.tsv
```

Layout files can either be _dynamic_ or _static_, and must be placed in
the respective directory hierarchy. Files directly within the `dynamic`
or `static` directories, can be:

 * a `.tsv` layout file, whose filename stem (part before the `.tsv`) is
   the _paradigm name_ that this layout corresponds to;
 * a subdirectory, whose filename is the _paradigm name_ this directory
   corresponds to. Within this subdirectory are `.tsv` layout files that
   indicate the different _size options_ available for this _paradigm
   name_.

> **Note**: the exact location for the root `layouts` file depends on
> the dictionary, however, this _should_ be with in the dictionary's
> resources directory. As of 2021-06-10, this means
> `src/CreeDictionary/res/layouts` for the `crkeng` dictionary.


Glossary
--------

### Dynamic vs. Static

A **dynamic paradigm layout** is one in which there are *placeholders*
for the `${lemma}`. At runtime, the placeholders are filled with
a provided lemma such that the placeholders can be substituted with
concrete wordforms, to be presented to users.

Dynamic paradigm layouts are useful for linguistic paradigms that are
_productive_ (i.e., used for systematically for a large number of
lexemes).

A **static paradigm layout** is one in which there are no placeholders.
All cells have their wordforms **explicitly** filled out. No
substitution is needed at runtime, so their contents will be presented
**as-is**.

Static paradigm layouts are useful for

### Paradigm Name

Which **linguistic paradigm** a wordform or entire lexeme belongs to.
This data should be provided by curated linguistic data during the
import process, although, historically, the paradigm name has been
assumed to be the specific word class of a lexeme. Because what exactly
determines a "paradigm" differs from language-to-language, a wordform's
`paradigm` name should be determined _before_ import time.
