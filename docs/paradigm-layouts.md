(paradigm_layouts)=
Paradigm layouts
================

This document describes `morphodict`'s **paradigm layout** package.

In the context of this document, a _paradigm_ is a **table of related
wordforms**. The exact nature of how the wordforms are related to one
another is not specified here — rather, that is for language experts to
specify.

The paradigm layout package is intended to work in conjunction with an
**analysis** and **generation** system, such as a **finite-state
transducer** (FST) for inflection. This enables **dynamic paradigm
layouts** (layouts with placeholders) to be used for a large number of
lexemes with the same _linguistic paradigm_.


Components of the paradigm system
---------------------------------

 - **paradigm layout files** (`.tsv` files) — specifies how to layout
   wordforms in one or more _panes_
 - the **layouts** directory structure — how to organize paradigm layout
   files on the filesystem. Subdirectories here indicate that a paradigm
   has multiple _sizes_
 - the **Paradigm Manager** — mediates access to all parsed paradigm
   layouts from the **layouts** directory, keeping track of the
   different _sizes_ of layout for each paradigm, as well as tying
   dynamic layouts to a transducer to produce inflections
 - the **relabelling system**, which substitutes **one or more tags**
   with user-facing labels


Paradigm layout files
---------------------

**Paradigm layouts files** describe how to arrange wordforms and labels
in a table format.

Layouts are tab-separated values (TSV) files, where each cell specifies
its role in the presented paradigm.

Paradigm layouts are:

 - a series of **panes** — a sub-table of related wordforms
 - each pane consists of a series of **rows**, which is either
   a **header** or a **content** row
 - each **content row** consists of a series of **cells**
 - a cell can either be a **row label**, a **column label**, or
   a **wordform cell**.

For example, this is a paradigm layout file for Swahili personal
pronouns (Derived from: <https://en.wikipedia.org/wiki/Swahili_grammar#Personal_pronouns>):

```
| Class	| Ind	| Comb | Suffix	| Gen | Suffix	| All
_ 1 _ Sg	mimi	-mi	_angu	--
_ 2 _ Sg	wewe	-we	-ako	--
_ 3 _ Sg	yeye	-ye	-ake	--
_ 1 _ Pl	sisi	-si	-etu	sisi
_ 2 _ Pl	nyinyi	-nyi	-enu	nyote
_ 3 _ Pl	wao	-o	-ao	wote
```

This example is a **static paradigm layout file** with one **pane**.
All but the first **row** have row labels, with two **tags** each. Each
column has a **column label**, with some having one tag, and some having
two tags. There are a three **missing forms** under the `All` column.

### Syntax


A **paradigm layout file** is a tab-separated values (TSV) file. A TSV
file is a series of *rows*. Each **row** is separated by a U+000A line
feed character. Note that this U+000A line feed is not considered to be
a part of the row in this specification.

The TSV file **SHOULD** have one trailing U+000A line feed character
after the last row.

The TSV file **MUST** be encoded in the **UTF-8** character encoding
scheme.

Each row is a series of _cells_. Cells are separated from each other by
one U+0009 CHARACTER TABULATION character (horizontal tab character).
Let `C` be the number of cells in a row. Let `T` be the number of tab
separators in a row. `C` is equal to `T + 1`.

Each row in the TSV file **SHOULD** contain the same number of tab
characters (each row has the same `T` tab separators). This includes
blank rows (see below).

> This is to facilitate display and editing of the TSV files in tools
> that expect an equal amount of tabs per row (e.g., the GitHub
> previewer, [VisiData][vd], common spreadsheet software,
> [PyCharm][pycharm-tsv]).

A paradigm layout file describes one or more _panes_, or a grouping of
rows. Each pane is separated by one blank row. A _blank row_ is
line that only consists of whitespace (including the tab character).
This is equivalent to a row that consists of `C` **empty** cells (see
below). A blank row **SHOULD** consist only of zero or more tab
separators.

A row can either be a:

 - **header row**: its first cell must be a **header label**, followed
   by whitespace.
 - **content row**: a row with any other kind of cells

A **label** is a single cell with one or more _tags_. Each tag
in the label begins with a **prefix**, a **space character**, and then
the tag proper. Each tag within a label is separated by a single space.

These are the different prefixes:

 - `#`: header labels: label that describes the entire pane it appears in
 - `_`: row labels: describes the row in the current pane
 - `|`: column labels: describes the column in the current pane

For example, `# Past # Indicative` is a **header** label that has two
**tags**: `Past` and `Indicative`. The **relabelling** system is
intended to interpret the tags to display a user-facing string.

A **cell** can be a **label** (as described above), an **empty** cell
(consisting of zero or more whitespace characters, a **missing** form
cell, consisting exactly of the string `--` or a **wordform** cell.
A parser **MUST** attempt interpreting the cell as a **label cell**, an
**empty cell**, or a **missing form** before it may interpret the cell
as a **wordform cell**.

A wordform cell is either a static wordform cell or a dynamic wordform
cell. A _dynamic_ wordform cell contains exactly one `${lemma}`
placeholder. The placeholder must be **filled** by an external system,
and the cell may be substituted with a generated wordform. A _static_
wordform cell does not contain a placeholder, and can be displayed to
users verbatim, without any substitution.
A paradigm layout is a _dynamic layout_ when it contains one or more
_dynamic wordform cells_. A paradigm layout is a _static layout_ when
it contains zero _dynamic_ wordform cells. A _dynamic layout_ **MUST**
be _filled_ before the layout is ready for presentation.

Aside from the presence or absence of the `${lemma}` placeholder, the
exact syntax of a wordform cell is defined by the implementation.

### Partial Grammar

Here is a partial [W3C Extended Backus-Naur Form (EBNF)][EBNF] grammar of
the layout file specification. The syntax of `WordformCell` and `Tag`
are implementation-dependent.

```
Layout ::= (Row NL)+

Row ::= BlankRow | HeaderRow | ContentRow

HeaderRow ::= HeaderLabel (TAB EmptyCell)*
ContentRow ::= ContentCell (TAB ContentCell)*

ContentCell ::= RowLabel
              | ColumnLabel
              | MissingForm
              | EmptyCell
              | WordformCell
BlankRow ::= EmptyCell (TAB EmptyCell)*

HeaderLabel ::= ('#' SP Tag)+
RowLabel ::= ('_' SP Tag)+
ColumnLabel ::= ('|' SP Tag)+
MissingForm ::= '-' '-'
EmptyCell ::= SP*

TAB ::= #x09
NL  ::= #x0A
SP  ::= #x20
```

> The variant of EBNF chosen can be visualized using following tool:
> <https://www.bottlecaps.de/rr/ui>

[EBNF]: https://www.w3.org/TR/2010/REC-xquery-20101214/#EBNFNotation

[vd]: https://www.visidata.org/
[pycharm-tsv]: https://www.jetbrains.com/help/pycharm/editing-csv-and-tsv-files.html

(where_paradigm_files_go)=

Where to place paradigm layout files
------------------------------------

Paradigm layout files are placed in the following directory structure
template:

```
layouts
├── {paradigm-name}
│   ├── {size-1}.tsv
│   ├── {size-2}.tsv
│   └── {size-3}.tsv
├── {paradigm-name}.tsv
└── {paradigm-name}.tsv
```

Files directly within the `layouts` directory, can be:

 * a `.tsv` layout file, whose filename stem (part before the `.tsv`) is
   the _paradigm name_ that this layout corresponds to; or
 * a subdirectory, whose filename is the _paradigm name_ this directory
   corresponds to. Within this subdirectory are `.tsv` layout files that
   indicate the different _size options_ available for this _paradigm
   name_.

This `layouts` directory should be placed in the dictionary-specific
`resources` directory, e.g., `src/arpeng/resources/layouts` for `arpeng`.

*Note*: as of 2021-08, the Cree layouts are still in their legacy location,
`src/CreeDictionary/res/layouts`. This is because the same layout files are
used by both Plains and Woods Cree. The intention to move them to
`src/cr_shared/resources/layouts` once code to support that is written.

How to configure paradigm sizes
-------------------------------

The order of the paradigm sizes are configured in Django's `settings.py`
with the `MORPHODICT_PARADIGM_SIZES` key. List **all** named paradigm
sizes in the order you wish for them to appear in this setting. For
example, if you have the sizes "basic", and "full", and want them to
appear in the order, make sure in your site's `settings.py` you have the
following:

```python
MORPHODICT_PARADIGM_SIZES = ["basic", "full"]
```
