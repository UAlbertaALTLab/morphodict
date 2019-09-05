"""
According to .layout files and .paradigm files. Generate pre-filled layout tables
"""
import csv
import glob
from os import path
from os.path import dirname
from pathlib import Path
from typing import Dict, List, Tuple, FrozenSet

import hfstol

from constants import LexicalCategory, ParadigmSize

# paradigm files names are inconsistent
PARADIGM_NAME_TO_IC = {
    "noun-na": LexicalCategory.NA,
    "noun-nad": LexicalCategory.NAD,
    "noun-ni": LexicalCategory.NI,
    "noun-nid": LexicalCategory.NID,
    "verb-ai": LexicalCategory.VAI,
    "verb-ii": LexicalCategory.VII,
    "verb-ta": LexicalCategory.VTA,
    "verb-ti": LexicalCategory.VTI,
}


def import_layouts(layout_file_dir: Path):
    layout_tables = dict()
    files = glob.glob(str(layout_file_dir / "*.tsv"))
    for file in files:

        name_wo_extension = str(path.split(file)[1]).split(".")[0]

        with open(file, "r") as f:
            lines = f.read().splitlines()

            layout_list = []

            assert len(lines) >= 1, "malformed layout file %s" % file
            celled_lines = list(map(lambda l: l.split("\t"), lines))
            # print(file, list(map(lambda cells: len(cells), celled_lines)))
            maximum_column_count = max(list(map(lambda c: len(c), celled_lines)))

            for cells in celled_lines:
                cells = list(map(lambda x: x.strip(), cells))
                if len(cells) == maximum_column_count:
                    layout_list.append(cells)
                else:
                    layout_list.append(
                        cells + ["" for _ in range(maximum_column_count - len(cells))]
                    )

            ic_str, size_str = name_wo_extension.split("-")
            layout_tables[
                (LexicalCategory(ic_str.upper()), ParadigmSize(size_str.upper()))
            ] = layout_list
    return layout_tables


def import_paradigms(
    paradigm_files_dir: Path
) -> Dict[LexicalCategory, Dict[FrozenSet[str], List[str]]]:
    paradigm_table = dict()
    files = glob.glob(str(paradigm_files_dir / "*.paradigm"))

    for file in files:
        name_wo_extension = str(path.split(file)[1]).split(".")[0]

        with open(file, "r") as f:
            lines = f.read().splitlines()

            class_paradigm: Dict[FrozenSet[str], List[str]] = dict()

            assert len(lines) >= 1, "malformed paradigm file %s" % file

            dash_line_index = 0
            while lines[dash_line_index] != "--":
                dash_line_index += 1

            for line_index in range(dash_line_index + 1, len(lines)):
                line = lines[line_index]
                if line and line[:2] != "{#":

                    component_tuple = tuple(map(lambda x: x.strip(), line.split("+")))

                    if component_tuple in class_paradigm:
                        class_paradigm[frozenset(component_tuple)].append(line)
                    else:
                        class_paradigm[frozenset(component_tuple)] = [line]

        paradigm_table[PARADIGM_NAME_TO_IC[name_wo_extension]] = class_paradigm

    return paradigm_table


class Combiner:
    _paradigm_tables: Dict[LexicalCategory, Dict[FrozenSet[str], List[str]]]
    """
    {InflectionCategory.NA:
        {{'N', 'I', 'Px1Sg', 'Pl'}: ['N+I+Px1Sg+Pl', 'I+N+Px1Sg+Pl']}
    }
    """
    _layout_tables: Dict[Tuple[LexicalCategory, ParadigmSize], List[List[str]]]
    """ how it looks like
    {(InflectionCategory.VAI, ParadigmSize.FULL): [['', '"PRESENT TENSE"', ''], ['', ': "Independent"', ': "Conjunct"'],
                      ['"1s"', 'Ind+Prs+1Sg', 'PV/e+*+Cnj+Prs+1Sg'], ['"2s"', 'Ind+Prs+2Sg', 'PV/e+*+Cnj+Prs+2Sg'],
                      ['"3s"', 'Ind+Prs+3Sg', 'PV/e+*+Cnj+Prs+3Sg'], ['"1p"', 'Ind+Prs+1Pl ', 'PV/e+*+Cnj+Prs+1Pl'],
                      ['"21"', 'Ind+Prs+12Pl', 'PV/e+*+Cnj+Prs+12Pl'], ['"2p"', 'Ind+Prs+2Pl', 'PV/e+*+Cnj+Prs+2Pl'],
                      ['"3p"', 'Ind+Prs+3Pl', 'PV/e+*+Cnj+Prs+3Pl'], ['"4"', 'Ind+Prs+4Sg/Pl', 'PV/e+*+Cnj+Prs+4Sg/Pl'],
                      ['"X"', 'Ind+Prs+X', 'PV/e+*+Cnj+Prs+X'], ['', '', ''], ['', '"PAST TENSE"', ''],
                      ['', ': "Independent"', ': "Conjunct"'], ['"1s"', 'Ind+Prt+1Sg', 'PV/e+*+Cnj+Prt+1Sg'],
                      ['"2s"', 'Ind+Prt+2Sg', 'PV/e+*+Cnj+Prt+2Sg'], ['"3s"', 'Ind+Prt+3Sg', 'PV/e+*+Cnj+Prt+3Sg'],
                      ['', '', ''], ['', '"FUTURE INTENTIONAL TENSE"', ''], ['', ': "Independent"', ': "Conjunct"'],
                      ['"1s"', 'Ind+Fut+Int+1Sg', 'PV/e+*+Cnj+Fut+Int+1Sg'],
                      ['"2s"', 'Ind+Fut+Int+2Sg', 'PV/e+*+Cnj+Fut+Int+2Sg'],
                      ['"3s"', 'Ind+Fut+Int+3Sg', 'PV/e+*+Cnj+Fut+Int+3Sg'], ['', '', ''],
                      ['', '"FUTURE DEFINITE TENSE"', ''], ['', ': "Independent"', ''], ['"1s"', 'Ind+Fut+Def+1Sg', ''],
                      ['"2s"', 'Ind+Fut+Def+2Sg', ''], ['"3s"', 'Ind+Fut+Def+3Sg', ''], ['', '', ''],
                      ['', '"FUTURE CONDITIONAL"', ''], ['"1s"', 'Fut+Cond+1Sg', ''], ['"2s"', 'Fut+Cond+2Sg', ''],
                      ['"3s"', 'Fut+Cond+3Sg', ''], ['', '', ''], ['', '"IMPERATIVE"', ''],
                      ['', ': "Immediate"', ': "Delayed"'], ['"2s"', 'Imp+Imm+2Sg', 'Imp+Del+2Sg'],
                      ['"21"', 'Imp+Imm+12Pl', 'Imp+Del+12Pl'], ['"2p"', 'Imp+Imm+2Pl', 'Imp+Del+2Pl']],
     (InflectionCategory.VAI, ParadigmSize.BASIC): [['', '"PRESENT TENSE"', ''], ['', ': "Independent"', ': "Conjunct"'],
                   ['"1s"', 'Ind+Prs+1Sg', 'PV/e+*+Cnj+Prs+1Sg'], ['"2s"', 'Ind+Prs+2Sg', 'PV/e+*+Cnj+Prs+2Sg'],
                   ['"3s"', 'Ind+Prs+3Sg', 'PV/e+*+Cnj+Prs+3Sg'], ['"1p"', 'Ind+Prs+1Pl ', 'PV/e+*+Cnj+Prs+1Pl'],
                   ['"21"', 'Ind+Prs+12Pl', 'PV/e+*+Cnj+Prs+12Pl'], ['"2p"', 'Ind+Prs+2Pl', 'PV/e+*+Cnj+Prs+2Pl'],
                   ['"3p"', 'Ind+Prs+3Pl', 'PV/e+*+Cnj+Prs+3Pl'], ['"4"', 'Ind+Prs+4Sg/Pl', 'PV/e+*+Cnj+Prs+4Sg/Pl'],
                   ['"X"', 'Ind+Prs+X', 'PV/e+*+Cnj+Prs+X'], ['', '', ''], ['', '"IMPERATIVE"', ''],
                   ['"Local"', ': "Immediate"', ': "Delayed"'], ['"2s"', 'Imp+Imm+2Sg', 'Imp+Del+2Sg'],
                   ['"21"', 'Imp+Imm+12Pl', 'Imp+Del+12Pl'], ['"2p"', 'Imp+Imm+2Pl', 'Imp+Del+2Pl']],

     ...

     }

    """

    def __init__(
        self,
        layout_absolute_dir: Path,
        paradigm_absolute_dir: Path,
        generator_hfstol_path: Path,
    ):
        """
        reads all of .tsv layout files into memory.
        inits fst generator

        :param layout_absolute_dir: the absolute directory of your .tsv layout files
        """
        self._paradigm_tables = import_paradigms(paradigm_absolute_dir)
        self._layout_tables = import_layouts(layout_absolute_dir)
        self._generator = hfstol.HFSTOL.from_file(generator_hfstol_path)

    @classmethod
    def default_filler(cls):
        """
        This returns a combiner that uses paradigm files, layout files, and hfstol files from `res` folder
        """
        res = Path(dirname(__file__)) / ".." / "res"
        return Combiner(
            res / "layouts",
            res / "paradigms",
            res / "fst" / "crk-normative-generator.hfstol",
        )

    def get_combined_table(
        self, category: LexicalCategory, paradigm_size: ParadigmSize
    ) -> List[List[str]]:
        """
        returns a paradigm table
        """

        if category is LexicalCategory.IPC or category is LexicalCategory.Pron:
            return []

        layout_table = self._layout_tables[(category, paradigm_size)]

        for rowInd, row in enumerate(layout_table):
            for colInd, cell in enumerate(row):

                if '"' not in cell and cell != "":  # it's a inflection form pattern

                    # see patterns in res/layouts/readme.md
                    replaced = ""
                    if "=" in cell:
                        replaced = "{{ lemma }}" + "+" + cell[1:]

                    elif "*" in cell:

                        replaced = cell.replace(
                            "*",
                            "%s%s" % ("{{ lemma }}", category.to_fst_output_style()),
                        )

                    else:
                        lookup_combination = set(cell.split("+"))
                        for combination, patterns in self._paradigm_tables[
                            category
                        ].items():
                            if lookup_combination < combination:
                                found = False
                                for pattern in patterns:
                                    if cell in pattern:
                                        replaced = pattern
                                        found = True
                                        break
                                if found:
                                    break
                    layout_table[rowInd][colInd] = replaced

        return layout_table


if __name__ == "__main__":
    filler = Combiner.default_filler()

    for ic in LexicalCategory:
        if ic is LexicalCategory.Pron or ic is LexicalCategory.IPC:
            continue
        for size in ParadigmSize:
            with open(
                path.join(
                    dirname(__file__),
                    "..",
                    "res",
                    "prefilled_layouts",
                    "%s-%s.useful.layout.tsv",
                )
                % (ic.value.lower(), size.value.lower()),
                "w",
                newline="",
            ) as file:
                a = filler.get_combined_table(ic, size)
                writer = csv.writer(file, delimiter="\t", quotechar="'")
                writer.writerows(a)
