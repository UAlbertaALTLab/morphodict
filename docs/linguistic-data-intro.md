# Summary

To get a working dictionary application, you’ll need linguistic data for
the morphodict code to use.

_**Note**: `sssttt` below refers to a [language pair abbreviation](sssttt)._

The specific kinds of required linguistic data are:

  - [A dictionary in importjson format](dictionary_data)

    Usually you will have or create the canonical dictionary data in some
    other format, and will write some code to extract and convert the
    required data from the canonical dictionary source to [the
    morphodict-specific importjson format](importjson-spec)

    The dictionary data is placed in `src/${sssttt}/resources/dictionary`;
    and loaded into the database via the `${sssttt}-manage importjsondict`
    command.

    Typically, there are two importjson files for each language:

      - a full dictionary which is *not checked in on github* because
        dictionaries tend not to be publicly redistributable,
      - and a small test dictionary [extracted from the full
        dictionary](building_test_dictionary_data), which is checked in for
        development and testing purposes.

  - Analyzer and generator FSTs in [hfstol format]

    These go in the `src/${sssttt}/resources/fst` directory,
    with the exact files configured in `settings.py`.

    A spell-relaxed analyzer FST is also strongly recommended, but if you
    do not have one, just re-use the one analyzer FST that you do have.

    We have first-class support for FSTs built in the
    [GiellaLT](https://giellalt.uit.no/) infrastructure, though other FSTs
    have also been used.

  - [Paradigm layout files](paradigm_layouts)

    These generally go in `src/${sssttt}/resources/layouts`; see [Where to
    place paradigm layout files](where_paradigm_files_go) for more
    specifics.

    If you are editing these be sure to set a
    [`DEBUG_PARADIGM_TABLES=True`](DEBUG_PARADIGM_TABLES) environment
    variable so you don’t have restart the python server to see updates.

  - Relabellings

    FSTs have tags that only linguists know the meaning of, and often these
    tags are abbreviated in ways that only the person who made that
    particular FST fully understands.

    Relabellings map FST tags to various classes of human-understandable
    labels.

    They also confusingly map Cree word class names and give definitions
    for preverbs sometimes too, but we need to do something different and
    better for other languages.

    For example, the Plains Cree FST tag `+1Sg` can be mapped to:

      - Linguistic short: “1s”

        Appears inside paradigm tables when “linguistic labels” are
        selected

      - Linguistic long: “Actor: 1st Person Singular”

        For an FST tag, it’s not clear where this is actually used; for a
        Cree word class name, this can appear in search results, or at the
        top of a word detail page

      - English: “I”

        Appears inside linguistic info popup on search results,
        and in paradigm tables when “English labels” are selected

      - nêhiyawêwin: “niya”

        Appears inside paradigm tables

      - Emoji: not applicable for `+1Sg`, but for a different example,
        `+N+A` maps to “🧑🏽”

        Appears in search results, or at the top of a word detail page

    In addition to mappings for individual FST tags, the relabelling files
    allow specifying labels for *combinations* of tags, so that `+1Sg+2SgO`
    can map to “1s → 2s”; however it’s not clear what/how the algorithm
    works for picking exactly which combination labels are used when there
    isn’t an exact match between all the analysis tags and a single
    combination label.

[hfstol format]: https://hdl.handle.net/10138/29370

For the items summarized above, more details are available below, or
may be requested.

# Quick note on TSV files

For editing tab-separated value aka TSV files, some people have had varying
levels of success with:

  - Excel, though it might need a byte-order mark at the start of a file to
    understand input on Windows, and might interpret things as formulas and
    mangle them, so check your diffs carefully when making pull requests

  - [Easy CSV
    Editor](https://apps.apple.com/us/app/easy-csv-editor/id1171346381?mt=12)
    works quite well, but is mac-only, and is not free

  - [visidata](https://www.visidata.org/) is a very powerful command-line
    data editing and exploration tool

  - There’s always vim for quick edits. You can do `:set ts=24` or
    something similar to make the tabs super obvious.

  - In PyCharm, an open TSV file actually has little Text / Data tabs at
    the bottom, which you can use to get a spreadsheet view!! However
    multiple people have had issues with this spreadsheet view not showing
    all the rows of a file.

Whatever you use to edit these TSV files, there is a handy script,
`scripts/reformat-altlabels`, that automatically evens out a TSV file
by making sure every row has the same number of tabs.

By default it will reformat every `altlab.tsv` file, but you can explicitly
give it the path to any TSV file on the command line.
