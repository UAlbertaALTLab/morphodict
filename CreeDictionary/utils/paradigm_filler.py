"""
fill a paradigm table according to a lemma
"""
import csv
from copy import deepcopy
from os.path import dirname
from pathlib import Path
from typing import Dict, List, Set, Tuple

import hfstol
from paradigm import Cell, EmptyRow, Layout, StaticCell, TitleRow, rows_to_layout
from utils import ParadigmSize, WordClass, shared_res_dir
from utils.paradigm_layout_combiner import Combiner

LayoutID = Tuple[WordClass, ParadigmSize]


class ParadigmFiller:
    _layout_tables: Dict[LayoutID, Layout]

    @staticmethod
    def _import_layouts(layout_dir, paradigm_dir) -> Dict[LayoutID, Layout]:
        """
        Combine .layout files and .paradigm files and import into memory

        :param paradigm_dir: the directory that has .paradigms files
        :param layout_dir: the directory that has .layout files and .layout.csv files
        """
        combiner = Combiner(layout_dir, paradigm_dir)

        layout_tables = {}

        for wc in WordClass:
            if not wc.has_inflections():
                continue
            for size in ParadigmSize:
                layout_tables[(wc, size)] = rows_to_layout(
                    combiner.get_combined_table(wc, size)
                )

        return layout_tables

    def __init__(
        self, layout_dir: Path, paradigm_dir: Path, generator_hfstol_path: Path
    ):
        """
        Combine .layout, .layout.csv, .paradigm files to paradigm tables of different sizes and store them in memory
        inits fst generator

        :param layout_dir: the directory for .layout and .layout.cvs files
        """
        self._layout_tables = self._import_layouts(layout_dir, paradigm_dir)
        self._generator = hfstol.HFSTOL.from_file(generator_hfstol_path)

    @classmethod
    def default_filler(cls):
        """
        Return a filler that uses .layout files, .paradigm files and the fst from the res folder
        """
        return ParadigmFiller(
            shared_res_dir / "layouts",
            shared_res_dir / "paradigms",
            shared_res_dir / "fst" / "crk-normative-generator.hfstol",
        )

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
        lookup_strings: List[str] = []
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

                    # It's a inflection form pattern
                    assert '"' not in cell
                    lookup_strings.append(cell.replace("{{ lemma }}", lemma))
                    string_locations.append((row_with_replacements, col_ind))

        # Generate ALL OF THE INFLECTIONS!
        results = self._generator.feed_in_bulk_fast(lookup_strings)

        # string locations and lookup_strings have parallel indices.
        assert len(string_locations) == len(lookup_strings)
        for i, location in enumerate(string_locations):
            row, col_ind = location
            analysis = lookup_strings[i]
            results_for_cell = sorted(results[analysis])
            # TODO: this should actually produce TWO rows!
            row[col_ind] = " / ".join(results_for_cell)

        return tables

    def inflect_all(self, lemma: str, wordclass: WordClass) -> Set[str]:
        """
        Return a set of all inflections for a particular lemma.
        """

        paradigm = self.fill_paradigm(lemma, wordclass, ParadigmSize.FULL)

        def find_all_inflections():
            for table in paradigm:
                for row in table:
                    if not isinstance(row, list):
                        continue
                    for cell in row:
                        if not isinstance(cell, str):
                            continue
                        if cell == "":
                            continue
                        # Assume this is an inflection
                        yield cell

        return set(find_all_inflections())
