"""
Compiles the source Neahttadigisánit .layout files and .paradigm files to a
"pre-filled" form.

This generate pre-filled paradigm layouts, which are subsequently used in the
web application.

DO NOT import this file in the Django web application.

See: paradigm_filler instead.
"""

import csv
import glob
import logging
from os import path
from os.path import dirname
from pathlib import Path
from typing import Dict, FrozenSet, List, Tuple

import hfstol

from constants import ParadigmSize, SimpleLC

# A raw paradigm layout from Neahttadigisánit.
Table = List[List[str]]

logger = logging.getLogger(__name__)

# paradigm files names are inconsistent
PARADIGM_NAME_TO_SLC = {
    "noun-na": SimpleLC.NA,
    "noun-nad": SimpleLC.NAD,
    "noun-ni": SimpleLC.NI,
    "noun-nid": SimpleLC.NID,
    "verb-ai": SimpleLC.VAI,
    "verb-ii": SimpleLC.VII,
    "verb-ta": SimpleLC.VTA,
    "verb-ti": SimpleLC.VTI,
}


LayoutTable = Dict[Tuple[SimpleLC, ParadigmSize], Table]


def import_layouts(layout_file_dir: Path) -> LayoutTable:
    layout_tables: LayoutTable = {}

    legacy_neahtta_layout_files = list(layout_file_dir.glob("*.layout"))
    simple_tsv_files = list(layout_file_dir.glob("*.layout.csv"))
    assert len(simple_tsv_files) > 0
    files = legacy_neahtta_layout_files + simple_tsv_files

    for layout_file in files:
        # Get rid of .layout or .csv
        stem, _dot, _extensions = layout_file.name.partition(".")
        *lc_str, size_str = stem.split("-")

        # Figure out if it's worth converting layout this layout.
        try:
            size = ParadigmSize(size_str.upper())
        except ValueError:
            # Unsupported "sizes" include: nehiyawewin, extended
            logger.info("unsupported paradigm size for %s", layout_file)
            continue

        lc = PARADIGM_NAME_TO_SLC["-".join(lc_str)]
        table = parse_layout(layout_file)

        if (lc, size) in layout_tables:
            logger.warning(
                "%s-%s already in table; replacing with %s", lc, size, layout_file
            )
        layout_tables[(lc, size)] = table

    return layout_tables


def parse_layout(layout_file: Path) -> Table:
    """
    Parses a layout and returns a "layout".
    """
    if layout_file.match("*.csv"):
        return parse_csv_layout(layout_file)
    else:
        assert layout_file.match("*.layout")
        return parse_legacy_layout(layout_file)


def parse_csv_layout(layout_file: Path) -> Table:
    """
    Parses a layout in the CSV/TSV format.
    """
    # Throw out the YAML header; we don't need it.
    _yaml_header, _divider, table_csv = layout_file.read_text(
        encoding="UTF-8"
    ).partition("\n--")

    lines = table_csv.splitlines()
    # the first line is part of the divider; get rid of it!
    del lines[0]

    # Not much parsing to do here: mostly
    table: Table = []
    last_row_len = None
    for line in lines:
        row = [cell.strip() for cell in line.split("\t")]
        table.append(row)
        row_len = len(row)
        assert (
            last_row_len is None or row_len == last_row_len
        ), f"expected length {last_row_len}; got: {row_len}"
        last_row_len = row_len

    return table


def parse_legacy_layout(layout_file: Path) -> Table:
    """
    Parses a legacy in the format the Neahttadigisánit expects.
    """
    lines = layout_file.read_text().splitlines()
    assert len(lines) >= 1, f"malformed layout file: {layout_file}"

    layout_list: Table = []

    # Figure out where the YAML header ends:
    dash_line_index = 0
    while lines[dash_line_index] != "--":
        dash_line_index += 1

    # file to -> rows with columns
    layout_lines = lines[dash_line_index + 1 :]
    celled_lines = [line.split("|")[1:-1] for line in layout_lines]
    maximum_column_count = max(len(line) for line in celled_lines)

    for cells in celled_lines:
        cells = [cell.strip() for cell in cells]
        assert len(cells) == maximum_column_count
        if all(cell == "" for cell in cells):
            layout_list.append([""] * maximum_column_count)
        else:
            layout_list.append(cells)

    return layout_list


def import_paradigms(
    paradigm_files_dir: Path,
) -> Dict[SimpleLC, Dict[FrozenSet[str], List[str]]]:
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

        paradigm_table[PARADIGM_NAME_TO_SLC[name_wo_extension]] = class_paradigm

    return paradigm_table


class Combiner:
    """
    Ties together the paradigm layouts, the expected forms from the .paradigm
    file, and a generator to create "pre-filled" layout files.

    This is a "compilation" step and happens before the server is started.
    Generally, this is when importing the raw files from Neahttadigisánit.

    That is, the combiner should NOT be used in the Django server.
    """

    _paradigm_tables: Dict[SimpleLC, Dict[FrozenSet[str], List[str]]]
    """
    {InflectionCategory.NA:
        {{'N', 'I', 'Px1Sg', 'Pl'}: ['N+I+Px1Sg+Pl', 'I+N+Px1Sg+Pl']}
    }
    """
    _layout_tables: Dict[Tuple[SimpleLC, ParadigmSize], Table]
    # todo: update how it looks like
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
        self, layout_dir: Path, paradigm_dir: Path, generator_hfstol_path: Path
    ):
        """
        Reads ALL of the .tsv layout files into memory and initializes the FST generator

        :param layout_dir: the absolute directory of your .tsv layout files
        """
        self._paradigm_tables = import_paradigms(paradigm_dir)
        self._layout_tables = import_layouts(layout_dir)
        self._generator = hfstol.HFSTOL.from_file(generator_hfstol_path)

    @classmethod
    def default_combiner(cls):
        """
        Returns a Combiner instance that uses the paradigm files, layout files, and hfstol files from `res` folder.
        """
        res = Path(dirname(__file__)) / ".." / "res"
        return Combiner(
            res / "layouts",
            res / "paradigms",
            res / "fst" / "crk-normative-generator.hfstol",
        )

    def get_combined_table(
        self, category: SimpleLC, paradigm_size: ParadigmSize
    ) -> List[List[str]]:
        """
        Return the appropriate layout.
        """

        if category is SimpleLC.IPC or category is SimpleLC.Pron:
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


def combine_layout_paradigm():
    combiner = Combiner.default_combiner()

    for ic in SimpleLC:
        if ic in (SimpleLC.Pron, SimpleLC.IPC, SimpleLC.IPV):
            continue
        for size in ParadigmSize:
            with open(
                path.join(
                    dirname(__file__), "..", "res", "prefilled_layouts", "%s-%s.tsv"
                )
                % (ic.value.lower(), size.value.lower()),
                "w",
                newline="",
            ) as file:
                a = combiner.get_combined_table(ic, size)
                writer = csv.writer(file, delimiter="\t", quotechar="'")
                writer.writerows(a)
