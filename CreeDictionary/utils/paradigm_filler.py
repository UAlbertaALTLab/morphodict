"""
fill a paradigm table according to a lemma
"""
import logging
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple, cast

from hfst_optimized_lookup import TransducerFile
from paradigm import (
    Cell,
    EmptyRow,
    InflectionCell,
    Layout,
    StaticCell,
    TitleRow,
    rows_to_layout,
)
from utils import ParadigmSize, WordClass, shared_res_dir
from utils.paradigm_layout_combiner import Combiner
from utils.types import ConcatAnalysis

LayoutID = Tuple[WordClass, ParadigmSize]

logger = logging.getLogger()


def import_frequency() -> Dict[ConcatAnalysis, int]:
    FILENAME = "attested-wordforms.txt"

    res: Dict[ConcatAnalysis, int] = {}
    lines = (shared_res_dir / FILENAME).read_text(encoding="UTF-8").splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            # Skip empty lines
            continue

        try:
            freq, _, *analyses = line.split()
        except ValueError:  # not enough value to unpack, which means the line has less than 3 values
            logger.warn(f'line "{line}" is broken in {FILENAME}')
        else:
            for analysis in analyses:
                res[ConcatAnalysis(analysis)] = int(freq)

    return res


class ParadigmFiller:
    _layout_tables: Dict[LayoutID, Layout]
    _generator: TransducerFile
    _frequency = import_frequency()

    @staticmethod
    def _import_layouts(layout_dir) -> Dict[LayoutID, Layout]:
        """
        Imports .layout files into memory.

        :param layout_dir: the directory that has .layout files and .layout.csv files
        """
        combiner = Combiner(layout_dir)

        layout_tables = {}

        for wc in WordClass:
            if not wc.has_inflections():
                continue
            for size in ParadigmSize:
                layout_tables[(wc, size)] = rows_to_layout(
                    combiner.get_combined_table(wc, size)
                )

        return layout_tables

    def __init__(self, layout_dir: Path, generator_hfstol_path: Path = None):
        """
        Combine .layout, .layout.csv, .paradigm files to paradigm tables of different sizes and store them in memory
        inits fst generator

        :param layout_dir: the directory for .layout and .layout.cvs files
        """
        self._layout_tables = self._import_layouts(layout_dir)

        if generator_hfstol_path is None:
            from shared import expensive

            self._generator = expensive.normative_generator
        else:
            self._generator = TransducerFile(generator_hfstol_path)

    @classmethod
    def default_filler(cls):
        """
        Return a filler that uses .layout files, .paradigm files and the fst from the res folder
        """
        return ParadigmFiller(shared_res_dir / "layouts")

    def fill_paradigm(
        self, lemma: str, category: WordClass, paradigm_size: ParadigmSize
    ) -> List[Layout]:
        """
        returns a paradigm table filled with words

        :returns: filled paradigm tables
        """
        # We want to lookup all of the inflections in bulk,
        # so set up some data structures that will allow us to:
        #  - store all unique things to lookup
        #  - remember which strings need to be replaced after lookups
        lookup_strings: List[ConcatAnalysis] = []
        string_locations: List[Tuple[List[Cell], int]] = []

        if category is WordClass.IPC or category is WordClass.Pron:
            return []

        layout_table = deepcopy(self._layout_tables[(category, paradigm_size)])

        tables: List[Layout] = [[]]

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
        for i, location in enumerate(string_locations):
            row, col_ind = location
            analysis = lookup_strings[i]
            results_for_cell = sorted(results[analysis])
            # TODO: this should actually produce TWO rows!
            inflection_cell = row[col_ind]
            assert isinstance(inflection_cell, InflectionCell)
            inflection_cell.inflection = " / ".join(results_for_cell)
            inflection_cell.frequency = self._frequency.get(analysis, 0)

        return tables

    def inflect_all_with_analyses(
        self, lemma: str, wordclass: WordClass
    ) -> Dict[ConcatAnalysis, Sequence[str]]:
        """
        Produces all known forms of a given word. Returns a mapping of analyses to their
        forms. Some analyses may have multiple forms. Some analyses may not generate a
        form.
        """
        analyses = self.expand_analyses(lemma, wordclass)
        return cast(
            Dict[ConcatAnalysis, Sequence[str]], self._generator.bulk_lookup(analyses)
        )

    def inflect_all(self, lemma: str, wordclass: WordClass) -> Set[str]:
        """
        Return a set of all inflections for a particular lemma.
        """
        all_inflections = self.inflect_all_with_analyses(lemma, wordclass).values()
        return set(form for word in all_inflections for form in word)

    def expand_analyses(self, lemma: str, wordclass: WordClass) -> Set[ConcatAnalysis]:
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
        analyses: Set[ConcatAnalysis] = set()
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
