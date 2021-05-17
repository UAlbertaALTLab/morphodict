from __future__ import annotations

"""
Fill a paradigm table with the inflections of a lemma.
"""

import logging
from copy import deepcopy
from pathlib import Path
from string import Template
from typing import Iterable, Literal, Optional, Sequence, Union, cast

from attr import attrib, attrs
from hfst_optimized_lookup import TransducerFile
from CreeDictionary.utils import ParadigmSize, WordClass, shared_res_dir
from CreeDictionary.utils.types import ConcatAnalysis

logger = logging.getLogger(__name__)

PARADIGM_NAME_TO_WC = {
    "noun-na": WordClass.NA,
    "noun-nad": WordClass.NAD,
    "noun-ni": WordClass.NI,
    "noun-nid": WordClass.NID,
    "verb-ai": WordClass.VAI,
    "verb-ii": WordClass.VII,
    "verb-ta": WordClass.VTA,
    "verb-ti": WordClass.VTI,
}

CORPUS_FREQUENCY_FILE = shared_res_dir / "corpus_frequency.txt"


##################################### Simple types #####################################

RawTable = list[list[str]]
Layouts = dict[tuple[WordClass, ParadigmSize], RawTable]
LayoutID = tuple[WordClass, ParadigmSize]


##################################### Main classes #####################################


class ParadigmFiller:
    def __init__(self, layout_dir: Path, generator_hfstol_path: Path = None):
        """
        Combine .layout, .layout.csv, .paradigm files to paradigm tables of different
        sizes and store them in memory.

        :param layout_dir: the directory for .layout and .layout.cvs files
        """
        self._layout_tables = self._import_layouts(layout_dir)
        self._frequency = import_frequency()

        if generator_hfstol_path is None:
            from CreeDictionary.shared import expensive

            self._generator = expensive.strict_generator
        else:
            self._generator = TransducerFile(generator_hfstol_path)

    @classmethod
    def default_filler(cls):
        """
        Return a filler that uses .layout files, .paradigm files and the fst from the
        res (resources) folder.
        """
        return ParadigmFiller(shared_res_dir / "layouts")

    def fill_paradigm(
        self, lemma: str, category: WordClass, paradigm_size: ParadigmSize
    ) -> list[Layout]:
        """
        Returns a paradigm table filled with word forms

        :returns: filled paradigm tables
        """

        if not category.has_inflections():
            return []

        # We want to lookup all of the inflections in bulk,
        # so set up some data structures that will allow us to:
        #  - store all unique things to lookup
        #  - remember which strings need to be replaced after lookups
        lookup_strings: list[ConcatAnalysis] = []
        string_locations: list[tuple[list[Cell], int]] = []

        layout_table = deepcopy(self._layout_tables[(category, paradigm_size)])

        tables: list[Layout] = [[]]

        for row in layout_table:
            if row is EmptyRow:
                # Create a new "pane"
                tables.append([])
            elif isinstance(row, TitleRow):
                tables[-1].append(row)
            else:
                assert isinstance(row, list)
                row_with_replacements = row.copy()
                tables[-1].append(row_with_replacements)
                for col_ind, cell in enumerate(row):
                    if isinstance(cell, StaticCell) or cell == "":
                        # We do nothing to static and empty cells.
                        continue
                    elif isinstance(cell, InflectionCell):
                        if cell.has_analysis:

                            lookup_strings.append(cell.create_concat_analysis(lemma))
                            string_locations.append((row_with_replacements, col_ind))
                    else:
                        raise ValueError("Unexpected Cell Type")

        # Generate ALL OF THE INFLECTIONS!
        results = self._generator.bulk_lookup(lookup_strings)

        # string_locations and lookup_strings have parallel indices.
        assert len(string_locations) == len(lookup_strings)
        for location, analysis in zip(string_locations, lookup_strings):
            row, col_ind = location
            results_for_cell = sorted(results[analysis])
            # TODO: this should actually produce TWO rows!
            inflection_cell = row[col_ind]
            assert isinstance(inflection_cell, InflectionCell)
            inflection_cell.inflection = " / ".join(results_for_cell)
            inflection_cell.frequency = self._frequency.get(analysis, 0)

        return tables

    def inflect_all_with_analyses(
        self, lemma: str, wordclass: WordClass
    ) -> dict[ConcatAnalysis, Sequence[str]]:
        """
        Produces all known forms of a given word. Returns a mapping of analyses to their
        forms. Some analyses may have multiple forms. Some analyses may not generate a
        form.
        """
        analyses = self.expand_analyses(lemma, wordclass)
        return cast(
            dict[ConcatAnalysis, Sequence[str]], self._generator.bulk_lookup(analyses)
        )

    def inflect_all(self, lemma: str, wordclass: WordClass) -> set[str]:
        """
        Return a set of all inflections for a particular lemma.
        """
        all_inflections = self.inflect_all_with_analyses(lemma, wordclass).values()
        return set(form for word in all_inflections for form in word)

    def expand_analyses(self, lemma: str, wordclass: WordClass) -> set[ConcatAnalysis]:
        """
        Given a lemma and its word class, return a set of all analyses that we could
        generate, but do not actually generate anything!
        """
        # I just copy-pasted the code from fill_paradigm() and edited it.
        # I'm sure we could refactor using the Template Method pattern or even Visitor
        # pattern to reduce code duplication, but I honestly think it's not worth it in
        # this situation.
        layout_table = self._layout_tables[(wordclass, ParadigmSize.LINGUISTIC)]

        # Find all of the analyses strings in the table:
        analyses: set[ConcatAnalysis] = set()
        for row in layout_table:
            if row is EmptyRow or isinstance(row, TitleRow):
                continue

            assert isinstance(row, list)
            for cell in row:
                if isinstance(cell, StaticCell) or cell == "":
                    continue
                elif isinstance(cell, InflectionCell):
                    if not cell.has_analysis:
                        continue
                    analysis = cell.create_concat_analysis(lemma)
                    analyses.add(analysis)
                else:
                    raise ValueError("Unexpected cell type")

        return analyses

    @staticmethod
    def _import_layouts(layout_dir) -> dict[LayoutID, Layout]:
        """
        Imports .layout files into memory.

        :param layout_dir: the directory that has .layout files and .layout.csv files
        """
        layout_tables = {}
        layouts = import_layouts(layout_dir)

        for wc in WordClass:
            if not wc.has_inflections():
                continue

            for size in ParadigmSize:
                layout_tables[(wc, size)] = rows_to_layout(layouts[wc, size])

        return layout_tables


################################## Table/Pane classes ##################################


class EmptyRowType:
    """
    A completely empty row! Singleton.
    """

    # Do a bunch of stuff to make this an empty row.
    _instance: EmptyRowType

    def __new__(cls) -> EmptyRowType:
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "EmptyRowType"

    def __deepcopy__(self, _memo) -> EmptyRowType:
        return self

    def __copy__(self) -> EmptyRowType:
        return self

    def __reduce__(self):
        return EmptyRowType, ()


EmptyRow = EmptyRowType()


@attrs
class TitleRow:
    """
    A row containing only a title -- no inflections of table headers.
    """

    title = attrib(type=str)
    span = attrib(type=int)

    # Makes it so that the Django template can easily determine that this is a
    # title:
    is_title = True


class StaticCell:
    """
    A cell that undergoes no change in the when rendering a layout to a
    paradigm.
    """

    is_heading: bool = False
    is_label = False

    text: str

    def __str__(self) -> str:
        return self.text


@attrs(frozen=True)
class Label(StaticCell):
    """
    A title in the rendered paradigm.
    """

    is_label = True
    text = attrib(type=str)


@attrs(frozen=True)
class Heading(StaticCell):
    """
    A section header in the rendered paradigm.
    """

    is_heading = True
    text = attrib(type=str)


# frozen=False is a reminder that the inflection is default as None and generated later
# inflection related info like inflection frequency is also generated later
@attrs(frozen=False, auto_attribs=True, eq=False, repr=False)
class InflectionCell:
    # the analysis of the inflection (with the lemma to be filled out)
    # It looks like for example "${lemma}+TAG+TAG+TAG", "TAG+${lemma}+TAG+TAG"
    analysis: Optional[Template] = None

    # the inflection to be generated
    inflection: Optional[str] = None

    # the frequency of the inflection in the corpus
    frequency: Optional[int] = None

    @property
    def has_analysis(self):
        return self.analysis is not None

    def __eq__(self, other) -> bool:
        # N.B., string.Template needs to be checked directly :/
        return isinstance(other, InflectionCell) and (
            (
                self.analysis is not None
                and other.analysis is not None
                and self.analysis.template == other.analysis.template
                and self.inflection == other.inflection
                and self.frequency == other.frequency
            )
            or (self.analysis is None and other.analysis is None)
        )

    def __repr__(self) -> str:
        if self.inflection or self.frequency and self.analysis is None:
            return super().__repr__()

        if self.analysis:
            analysis_repr = f"Template({self.analysis.template!r}"
        else:
            analysis_repr = "None"

        return f"{type(self).__name__}(analysis={analysis_repr})"

    def create_concat_analysis(self, lemma: str) -> ConcatAnalysis:
        """
        Fills in the analysis. Useful if you want to inflect this cell.

        >>> cell = InflectionCell.from_raw_nds_cell("{{ lemma }}+V+II+Ind+3Sg")
        >>> cell.create_concat_analysis("mispon")
        'mispon+V+II+Ind+3Sg'
        """
        assert self.analysis is not None

        return ConcatAnalysis(self.analysis.substitute(lemma=lemma))

    @classmethod
    def from_raw_nds_cell(cls, raw_cell: str) -> "InflectionCell":
        """
        Generates an InflectionCell from a NDS-style (legacy) template format.
        """
        return cls(Template(raw_cell.replace("{{ lemma }}", "${lemma}")))


Cell = Union[InflectionCell, StaticCell, Literal[""]]
Row = Union[list[Cell], EmptyRowType, TitleRow]
# TODO: Make a class for a list of rows (a Pane)
Layout = list[Row]


################################## Internal functions ##################################


def import_frequency() -> dict[ConcatAnalysis, int]:
    # TODO: store this in the database, rather than as a source file
    # TODO: make a management command that updates wordform frequencies

    res: dict[ConcatAnalysis, int] = {}
    lines = CORPUS_FREQUENCY_FILE.read_text(encoding="UTF-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            # Skip empty lines
            continue

        try:
            freq, _, *analyses = line.split()
        except ValueError:
            # not enough value to unpack, which means the line has less than 3 values
            logger.warning(f'line "{line}" is broken in {CORPUS_FREQUENCY_FILE}')
        else:
            for analysis in analyses:
                res[ConcatAnalysis(analysis)] = int(freq)

    return res


def import_layouts(layout_file_dir: Path) -> Layouts:
    layout_tables: Layouts = {}

    files = list(layout_file_dir.glob("*.layout.tsv"))

    if len(files) == 0:
        raise ValueError(
            f"Could not find any applicable layout files in {layout_file_dir}"
        )

    for layout_file in files:
        # Get rid of .layout
        stem, _dot, _extensions = layout_file.name.partition(".")
        *wc_str, size_str = stem.split("-")

        # Figure out if it's worth converting this layout.
        try:
            size = ParadigmSize(size_str.upper())
        except ValueError:
            # Unsupported "sizes" include: nehiyawewin, extended
            logger.info("unsupported paradigm size for %s", layout_file)
            continue

        try:
            wc = PARADIGM_NAME_TO_WC["-".join(wc_str)]
        except KeyError:
            logger.info("ignoring unsupported layout wordclass: %s", layout_file)
            continue

        table = parse_layout(layout_file)

        if (wc, size) in layout_tables:
            logger.warning(
                "%s-%s already in table; replacing with %s", wc, size, layout_file
            )
        layout_tables[(wc, size)] = table

    return layout_tables


def parse_layout(layout_file: Path) -> RawTable:
    """
    Parses a layout in the TSV format.
    """
    assert layout_file.match("*.tsv")

    file_text = layout_file.read_text(encoding="UTF-8")

    if "\n--\n" in file_text:
        raise NotImplementedError("NDS YAML header not supported")

    table: RawTable = []

    lines = file_text.splitlines()
    for row_no, line in enumerate(lines, start=1):
        line = line.rstrip()
        row = [cell.strip() for cell in line.split("\t")]
        table.append(row)

    return table


def rows_to_layout(rows: Iterable[list[str]]) -> Layout:
    """
    Takes rows (e.g., from a TSV file), and creates a well-formatted layout
    file.
    """
    layout: Layout = []

    max_row_length = len(max(rows, key=len))

    for raw_row in rows:
        row = determine_cells(raw_row)
        row.extend([""] * (max_row_length - len(row)))

        has_content = False
        n_labels = 0
        last_label: Optional[str] = None

        for cell in row:
            if isinstance(cell, Label):
                n_labels += 1
                last_label = cell.text
            elif cell != "":
                has_content = True

        if not has_content and n_labels == 0:
            layout.append(EmptyRow)
        elif not has_content and n_labels == 1:
            assert last_label is not None
            layout.append(TitleRow(last_label, span=len(row)))
        else:
            layout.append(row)

    return layout


def does_raw_row_has_row_header(raw_row: list[str]) -> bool:
    """
    does the row host inflection or not?
    """

    # we check if the row has a "left aligned heading"

    for i, raw_cell in enumerate(raw_row):

        if (
            raw_cell.startswith('"')
            and raw_cell.endswith('"')
            or raw_cell.startswith(":")
        ):
            return i == 0

    return False


def determine_cells(raw_row: list[str]) -> list[Cell]:
    has_row_header = does_raw_row_has_row_header(raw_row=raw_row)
    cells: list[Cell] = []

    for raw_cell in raw_row:
        cell: Cell

        if raw_cell.startswith('"') and raw_cell.endswith('"'):
            # This will be something like:
            #   "Something is happening now"
            #   "Speech act participants"
            assert len(raw_cell) > 2
            cell = Label(raw_cell[1:-1])
        elif raw_cell.startswith(":"):
            # This will be something like:
            #   : "ê-/kâ- word"
            #   : "ni-/ki- word"
            _colon, content, _empty = raw_cell.split('"')
            cell = Heading(content)
        else:
            raw_cell = raw_cell.strip()
            if raw_cell == "":
                if has_row_header:
                    cell = InflectionCell()
                else:
                    cell = ""
            else:
                # "{{ lemma }}" is a proprietary format
                cell = InflectionCell.from_raw_nds_cell(raw_cell)

        cells.append(cell)
    return cells
