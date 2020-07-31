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
from utils import ParadigmSize, WordClass
from utils.shared_res_dir import shared_res_dir

# A raw paradigm layout from Neahttadigisánit.
Table = List[List[str]]

logger = logging.getLogger(__name__)

# paradigm files names are inconsistent
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


LayoutTable = Dict[Tuple[WordClass, ParadigmSize], Table]


def import_layouts(layout_file_dir: Path) -> LayoutTable:
    layout_tables: LayoutTable = {}

    legacy_neahtta_layout_files = list(layout_file_dir.glob("*.layout"))
    simple_csv_files = list(layout_file_dir.glob("*.layout.csv"))
    simple_tsv_files = list(layout_file_dir.glob("*.layout.tsv"))

    files = legacy_neahtta_layout_files + simple_csv_files + simple_tsv_files
    if len(files) == 0:
        raise ValueError(
            f"Could not find any applicable layout files in {layout_file_dir}"
        )

    for layout_file in files:
        # Get rid of .layout or .csv
        stem, _dot, _extensions = layout_file.name.partition(".")
        *wc_str, size_str = stem.split("-")

        # Figure out if it's worth converting layout this layout.
        try:
            size = ParadigmSize(size_str.upper())
        except ValueError:
            # Unsupported "sizes" include: nehiyawewin, extended
            logger.info("unsupported paradigm size for %s", layout_file)
            continue

        wc = PARADIGM_NAME_TO_WC["-".join(wc_str)]
        table = parse_csv_layout(layout_file)

        if (wc, size) in layout_tables:
            logger.warning(
                "%s-%s already in table; replacing with %s", wc, size, layout_file
            )
        layout_tables[(wc, size)] = table

    return layout_tables


def parse_csv_layout(layout_file: Path) -> Table:
    """
    Parses a layout in the CSV/TSV format.
    """
    file_text = layout_file.read_text(encoding="UTF-8")

    return _parse_csv_layout(file_text.splitlines())


def _parse_csv_layout(lines: List[str]) -> Table:
    # Not much parsing to do here: mostly trimming trailing empty cells
    table: Table = []
    for line in lines:
        line = line.rstrip()
        row = [cell.strip() for cell in line.split("\t")]
        table.append(row)

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
) -> Dict[WordClass, Dict[FrozenSet[str], List[str]]]:
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

        paradigm_table[PARADIGM_NAME_TO_WC[name_wo_extension]] = class_paradigm

    return paradigm_table


class Combiner:
    """
    Ties together the paradigm layouts, the expected forms from the .paradigm
    file, and a generator to create "pre-filled" layout files.

    This is a "compilation" step and happens before the server is started.
    Generally, this is when importing the raw files from Neahttadigisánit.

    That is, the combiner should NOT be used in the Django server.
    """

    _layout_tables: Dict[Tuple[WordClass, ParadigmSize], Table]

    def __init__(self, layout_dir: Path):
        """
        Reads ALL of the .tsv layout files into memory and initializes the FST generator

        :param layout_dir: the absolute directory of your .tsv layout files
        """
        self._layout_tables = import_layouts(layout_dir)

    @classmethod
    def default_combiner(cls):
        """
        Returns a Combiner instance that uses the paradigm files, layout files, and hfstol files from `res` folder.
        """
        res = Path(dirname(__file__)) / ".." / "res"
        return Combiner(res / "layouts")

    def get_combined_table(
        self, category: WordClass, paradigm_size: ParadigmSize
    ) -> List[List[str]]:
        """
        Return the appropriate layout.
        """

        if category is WordClass.IPC or category is WordClass.Pron:
            return []

        # Can be returned unchanged!
        return self._layout_tables[(category, paradigm_size)]
