f"""
Compiles the .layout files into a "pre-filled" form.  The pre-filled paradigm layouts
are subsequently used in the web application.
Compiles the .layout files into a "pre-filled" form.  The pre-filled paradigm layouts
are subsequently used in the web application.

See also: paradigm_filler.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from utils import ParadigmSize, WordClass

# A raw paradigm layout:
Table = List[List[str]]

# Maps wordclass + size to a table
LayoutTable = Dict[Tuple[WordClass, ParadigmSize], Table]

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

logger = logging.getLogger(__name__)


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
    Parses a layout in the TSV format.
    """
    assert layout_file.match("*.tsv")

    file_text = layout_file.read_text(encoding="UTF-8")

    if "\n--\n" in file_text:
        raise NotImplementedError("NDS YAML header not supported")

    table: Table = []

    lines = file_text.splitlines()
    for row_no, line in enumerate(lines, start=1):
        line = line.rstrip()
        row = [cell.strip() for cell in line.split("\t")]
        table.append(row)

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
