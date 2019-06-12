import glob
import re
import shutil
import subprocess
from os import path
from pprint import pprint
from subprocess import PIPE
from typing import Dict, Any, List, Tuple, FrozenSet


# paradigm files names are inconsistent
PARADIGM_NAMING_CONVERSION = {
    "noun-na": "na",
    "noun-nad": "nad",
    "noun-ni": "ni",
    "noun-nid": "nid",
    "verb-ai": "vai",
    "verb-ii": "vii",
    "verb-ta": "vta",
    "verb-ti": "vti",
}


def convert_layout_name_to_layout_class(layout_name: str) -> List[str]:
    """
    :param layout_name: eg. "vii-full" "vai-basic"
    :returns: eg. ['V', 'II'], ['N', 'I', 'D']

    """
    layout_class = re.match("(nad?|nid?|vai|vii|vt[ai]|ipc)", layout_name).groups()[0]
    if layout_class[0] == "n":
        return list(layout_class.upper())
    elif layout_class[0] == "v":
        return ["V", layout_class[1:].upper()]
    else:
        return ["IPC"]


HFSTOL_PATH = shutil.which("hfst-optimized-lookup")
if HFSTOL_PATH is None:
    raise ImportError(
        "hfst-optimized-lookup is not installed.\n"
        "Please install the HFST suite on your system "
        "before importing this module.\n"
        "See: https://github.com/hfst/hfst#installation"
    )


def import_layouts(absolute_dir):
    layout_tables = dict()
    files = glob.glob(path.join(absolute_dir, "*.tsv"))
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
            layout_tables[name_wo_extension] = layout_list
    return layout_tables


def import_paradigms(
    paradigm_absolute_dir
) -> Dict[str, Dict[FrozenSet[str], List[str]]]:
    paradigm_table = dict()
    files = glob.glob(path.join(paradigm_absolute_dir, "*.paradigm"))

    for file in files:

        name_wo_extension = str(path.split(file)[1]).split(".")[0]

        with open(file, "r") as f:
            lines = f.read().splitlines()

            class_paradigm = dict()

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

        paradigm_table[PARADIGM_NAMING_CONVERSION[name_wo_extension]] = class_paradigm

    return paradigm_table


class ParadigmFiller:
    paradigm_table: Dict[str, Dict[FrozenSet[str], List[str]]]
    """
    {'na':
        {{'N', 'I', 'Px1Sg', 'Pl'}: ['N+I+Px1Sg+Pl', 'I+N+Px1Sg+Pl']}
    }
    """
    layout_tables: Dict[str, List[List[str]]]
    """ how it looks like
    {'vai-extended': [['', '"PRESENT TENSE"', ''], ['', ': "Independent"', ': "Conjunct"'],
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
     'vai-basic': [['', '"PRESENT TENSE"', ''], ['', ': "Independent"', ': "Conjunct"'],
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
        layout_absolute_dir: str,
        paradigm_absolute_dir: str,
        generator_hfstol_absolute_path: str,
    ):
        """
        reads all of .tsv layout files into memory.
        inits fst generator

        :param layout_absolute_dir: the absolute directory of your .tsv layout files
        """
        self.paradigm_table = import_paradigms(paradigm_absolute_dir)
        self.layout_tables = import_layouts(layout_absolute_dir)
        self.generator_hfstol_absolute_path = generator_hfstol_absolute_path

        # print(list(self.layout_tables.keys()))

    @classmethod
    def default_filler(cls):
        base = path.split(__file__)[0]
        return ParadigmFiller(
            path.join(base, "layouts"),
            path.join(base, "paradigm"),
            path.join(base, "crk-normative-generator.hfstol"),
        )

    def fill_paradigm(self, table_name: str, lemma: str) -> List[List[str]]:
        """
        returns a paradigm table filled with words

        :param lemma: lemma (allows non exact spelling)
        :param table_name: tsv file of the layout, for example 'vai-basic'
        :returns: filled paradigm table
        """
        lookup_strings: List[str] = []
        string_locations: List[Tuple[int, int]] = []

        layout_class = convert_layout_name_to_layout_class(table_name)

        if layout_class[0] == "IPC":
            return []

        layout_table = self.layout_tables[table_name]

        for rowInd, row in enumerate(layout_table):
            for colInd, cell in enumerate(row):
                if '"' not in cell and cell != "":  # it's a inflection form pattern

                    # see patterns in readme.md

                    if "=" in cell:
                        lookup_strings.append(lemma + "+" + cell[1:])
                        string_locations.append((rowInd, colInd))

                    elif "*" in cell:

                        lookup_strings.append(
                            cell.replace("*", "%s+%s" % (lemma, "+".join(layout_class)))
                        )
                        # print(lookup_strings)
                        string_locations.append((rowInd, colInd))
                    else:
                        lookup_combination = set(cell.split("+"))
                        # print(lookup_combination)
                        # print(self.paradigm_table[table_name.split("-")[0]])
                        # print(lookup_combination)
                        for combination, patterns in self.paradigm_table[
                            table_name.split("-")[0]
                        ].items():
                            if {"Prs", "Ind", "1Pl"} < lookup_combination:
                                pass
                            # print(lookup_combination)
                            # print(combination)
                            if lookup_combination < combination:
                                # print(combination)
                                found = False
                                for pattern in patterns:
                                    # print(pattern)
                                    if cell in pattern:

                                        lookup_strings.append(
                                            pattern.replace("{{ lemma }}", lemma)
                                        )
                                        string_locations.append((rowInd, colInd))
                                        found = True
                                        break
                                if found:
                                    break

        results = self.generate(lookup_strings)
        assert len(set(string_locations)) == len(
            string_locations
        ), "boom, one layout cell multiple patterns?? this shouldn't happen"

        for i, locations in enumerate(string_locations):
            row_ind, col_ind = locations
            layout_table[row_ind][col_ind] = " / ".join(results[lookup_strings[i]])

        return layout_table

    def generate(self, analyses):
        """
        Given one or more analyses, returns a dictionary with keys being the input
        parameters, and values being the set of returned analyses.

        For best performance, call this on as many many analyses as possible — use
        a big list of analyses!

        Args:
            analyses (iterable of str): zero or more of analyses to
                                        convert into word forms
        Kwargs:
            fst_path (str): path to the *.hfstol file

        Returns:
            dict of analyses (keys) and a set of its word forms (values)
        """

        # hfst-optimized-lookup expects each analysis on a separate line:
        lines = "\n".join(analyses).encode("UTF-8")

        status = subprocess.run(
            [
                HFSTOL_PATH,
                "--quiet",
                "--pipe-mode",
                self.generator_hfstol_absolute_path,
            ],
            input=lines,
            stdout=PIPE,
            stderr=PIPE,
            shell=False,
        )

        analysis2wordform = {}
        for line in status.stdout.decode("UTF-8").splitlines():
            # Remove extraneous whitespace.
            line = line.strip()
            # Skip empty lines.
            if not line:
                continue

            # Each line will be in this form:
            #   verbatim-analysis \t wordform
            # where \t is a tab character
            # e.g.,
            #   nôhkom+N+A+D+Px1Pl+Sg \t nôhkominân
            # If the analysis doesn't match, the transduction will have +?:
            # e.g.,
            #   nôhkom+N+A+I+Px1Pl+Sg	nôhkom+N+A+I+Px1Pl+Sg	+?
            analysis, word_form, *rest = line.split("\t")

            # ensure the set exists:
            if analysis not in analysis2wordform:
                analysis2wordform[analysis] = set()

            # Generating this word form failed!
            if "+?" in rest:
                continue

            analysis2wordform[analysis].add(word_form)

        return analysis2wordform


if __name__ == "__main__":
    pass
    # p = ParadigmFiller("layouts/", "paradigm/", "crk-normative-generator.hfstol")
    #
    # d = p.fill_paradigm("vai-full", "itwêw")
    #
    # # d = p.generate(['mowêw+V+TA+Ind+Prs+3Pl+1SgO'])
    # pprint(d)

    # print(convert_layout_name_to_layout_class("nid-full"))

    paradigm_filler = ParadigmFiller.default_filler()
    print(paradigm_filler.layout_tables)
