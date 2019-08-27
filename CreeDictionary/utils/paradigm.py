"""
According to .layout files and .paradigm files. Generate paradigm tables filled with fst analyses for each `InflectionCategory`
"""
import csv
import glob
from os import path
from os.path import dirname
from pathlib import Path
from typing import Dict, List, Tuple

import hfstol

from constants import LexicalCategory, ParadigmSize


def import_layouts(layout_file_dir: Path):
    """
    >>> a = import_layouts(Path(dirname(__file__)) / '..' / 'res' / 'prefilled_layouts')
    >>> a[(LexicalCategory.VTA, ParadigmSize.BASIC)]
    [['', '"PRESENT TENSE"', ''], ['"Speech Act Participants"', ': "Independent"', ': "Conjunct"'], ['"2s → 1s"', '{{ lemma }}+V+TA+Ind+Prs+2Sg+1SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+2Sg+1SgO'], ['"1s → 2s"', '{{ lemma }}+V+TA+Ind+Prs+1Sg+2SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+1Sg+2SgO'], ['', '', ''], ['"Mixed participants"', ': "Independent"', ': "Conjunct"'], ['"1s → 3s"', '{{ lemma }}+V+TA+Ind+Prs+1Sg+3SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+1Sg+3SgO'], ['"2s → 3s"', '{{ lemma }}+V+TA+Ind+Prs+2Sg+3SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+2Sg+3SgO'], ['"3s → 1s"', '{{ lemma }}+V+TA+Ind+Prs+3Sg+1SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+3Sg+1SgO'], ['"3s → 2s"', '{{ lemma }}+V+TA+Ind+Prs+3Sg+2SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+3Sg+2SgO'], ['', '', ''], ['"Third person participants"', ': "Independent"', ': "Conjunct"'], ['"3s → 4"', '{{ lemma }}+V+TA+Ind+Prs+3Sg+4Sg/PlO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+3Sg+4Sg/PlO'], ['"4 → 3s"', '{{ lemma }}+V+TA+Ind+Prs+4Sg/Pl+3SgO', 'PV/e+{{ lemma }}+V+TA+Cnj+Prs+4Sg/Pl+3SgO'], ['', '', ''], ['', '"IMPERATIVE"', ''], ['', '"Immediate"', ''], ['"2s → 1s"', '{{ lemma }}+V+TA+Imp+Imm+2Sg+1SgO', ''], ['"2s → 3s"', '{{ lemma }}+V+TA+Imp+Imm+2Sg+3SgO', '']]
    """
    layout_tables = dict()
    files = glob.glob(str(layout_file_dir / "*.tsv"))
    for file in files:

        name_wo_extension = str(path.split(file)[1]).split(".")[0]

        with open(file, "r") as f:

            reader = csv.reader(f, delimiter="\t", quotechar="'")
            layout_list = list(reader)
            ic_str, size_str = name_wo_extension.split("-")
            layout_tables[
                (LexicalCategory(ic_str.upper()), ParadigmSize(size_str.upper()))
            ] = layout_list
    return layout_tables


class ParadigmFiller:
    _layout_tables: Dict[Tuple[LexicalCategory, ParadigmSize], List[List[str]]]

    def __init__(self, layout_dir: Path, generator_hfstol_path: Path):
        """
        reads all of .tsv layout files into memory.
        inits fst generator

        :param layout_dir: the directory for useful.layout.tsv files
        """
        self._layout_tables = import_layouts(layout_dir)
        self._generator = hfstol.HFSTOL.from_file(generator_hfstol_path)

    @classmethod
    def default_filler(cls):
        """
        Return a filler that uses prefilled layout files and fst from the res folder
        """
        res = Path(dirname(__file__)) / ".." / "res"
        return ParadigmFiller(
            res / "prefilled_layouts", res / "fst" / "crk-normative-generator.hfstol"
        )

    def fill_paradigm(
        self, lemma: str, category: LexicalCategory, paradigm_size: ParadigmSize
    ) -> List[List[str]]:
        """
        returns a paradigm table filled with words

        :returns: filled paradigm table
        """
        lookup_strings: List[str] = []
        string_locations: List[Tuple[int, int]] = []

        if category is LexicalCategory.IPC or category is LexicalCategory.Pron:
            return []

        layout_table = self._layout_tables[(category, paradigm_size)]

        for rowInd, row in enumerate(layout_table):
            for colInd, cell in enumerate(row):
                if '"' not in cell and cell != "":  # it's a inflection form pattern
                    lookup_strings.append(cell.replace("{{ lemma }}", lemma))
                    string_locations.append((rowInd, colInd))

        results = self._generator.feed_in_bulk_fast(lookup_strings)

        for i, locations in enumerate(string_locations):
            row_ind, col_ind = locations
            layout_table[row_ind][col_ind] = " / ".join(
                sorted(results[lookup_strings[i]])
            )

        return layout_table
