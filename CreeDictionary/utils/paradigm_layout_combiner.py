"""
Compiles the .layout files into a "pre-filled" form.  The pre-filled paradigm layouts
are subsequently used in the web application.

See also: paradigm_filler.
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

    files = list(layout_file_dir.glob("*.layout.tsv"))

    if len(files) == 0:
        raise ValueError(
            f"Could not find any applicable layout files in {layout_file_dir}"
        )

    for layout_file in files:
        # Get rid of .layout
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
        table = parse_layout(layout_file)

        if (wc, size) in layout_tables:
            logger.warning(
                "%s-%s already in table; replacing with %s", wc, size, layout_file
            )
        layout_tables[(wc, size)] = table

    return layout_tables


def parse_layout(layout_file: Path) -> Table:
    """
    Parses a raw layout file.
    """
    assert layout_file.match("*.tsv")
    return parse_csv_layout(layout_file)


def parse_csv_layout(layout_file: Path) -> Table:
    """
    Parses a layout in the TSV format.
    """
    # Throw out the YAML header; we don't need it.
    file_text = layout_file.read_text(encoding="UTF-8")
    _yaml_header, _divider, table_csv = file_text.partition("\n--")

    if "\n--\n" not in file_text:
        return _parse_csv_layout(file_text.splitlines())

    raise NotImplementedError("NDS file format not supportted")


def _parse_csv_layout(lines: List[str]) -> Table:
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


# TODO: is this class even needed anymore?
class Combiner:
    """
    Ties together the paradigm layouts and a generator to create "pre-filled" layouts.
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
