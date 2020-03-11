"""
shared (expensive) instances
"""
import subprocess
from io import StringIO
from hfstol import HFSTOL
from typing import Set

from constants import Analysis
from utils import paradigm_filler as pf
from utils import shared_res_dir

paradigm_filler = pf.ParadigmFiller.default_filler()

# used in database building
descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)

# used in database building
strict_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-strict-analyzer.hfstol"
)

# used in database building
normative_generator = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-normative-generator.hfstol"
)


# class NormativeGenerator and class DescriptiveAnalyzer are used in search code.
# Since generator/analyzer from hfstol python package above breaks integration tests
# For details, see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120

# Pythonic singleton. The initialization creates a demonic hfstol process waiting to be used at any time
class DescriptiveAnalyzer:
    _instance = None

    def __init__(self):
        if DescriptiveAnalyzer._instance is None:
            # do initialization here
            self.proc = subprocess.Popen(
                args=[
                    "hfst-optimized-lookup",
                    "--quiet",
                    "--pipe-mode",
                    str(shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                universal_newlines=True,
            )
            DescriptiveAnalyzer._instance = self

    def analyze(self, cree: str) -> Set[Analysis]:
        return feed_to_hfstol_process(self.proc, cree)

    def __new__(cls, **kwargs):
        if cls._instance is None:
            _instance = super().__new__(cls, **kwargs)
        else:
            _instance = cls._instance
        return _instance


# Pythonic singleton. The initialization creates a demonic hfstol process waiting to be used at any time
class NormativeGenerator:
    _instance = None

    def __init__(self):
        if NormativeGenerator._instance is None:
            # do initialization here
            self.proc = subprocess.Popen(
                args=[
                    "hfst-optimized-lookup",
                    "--quiet",
                    "--pipe-mode",
                    str(shared_res_dir / "fst" / "crk-normative-generator.hfstol"),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                universal_newlines=True,
            )
            NormativeGenerator._instance = self

    def generate(self, analysis: Analysis) -> Set[str]:
        return feed_to_hfstol_process(self.proc, analysis)

    def __new__(cls, **kwargs):
        if cls._instance is None:
            _instance = super().__new__(cls, **kwargs)
        else:
            _instance = cls._instance
        return _instance


## helper function
def feed_to_hfstol_process(proc: subprocess.Popen, surface_form) -> set:

    # example output of the hfstol binary

    # $ hfst-optimized-lookup --quiet --pipe-mode CreeDictionary/res/fst/crk-descriptive-analyzer.hfstol
    # nipa (this is input line)
    # nipa\tnipâw+V+AI+Imp+Imm+2Sg
    #
    # niskak (this is input line)
    # niskak\tniska+N+A+Pl
    # niskak\tnîskâw+V+II+Cnj+Prs+3Sg
    #
    # c
    # c       c       +?
    #
    #
    #
    # EOF

    # two or more consecutive newlines signals the end of the output
    assert proc.stdin is not None
    proc.stdin.write(surface_form + "\n")
    proc.stdin.flush()

    results: Set[str] = set()

    consecutive_newline_count = 0

    assert proc.stdout is not None
    # ignore empty characters (consecutive white space characters from previous invocations)
    while 1:
        char = proc.stdout.read(1)
        if char.strip():
            line_buffer = char
            break

    while consecutive_newline_count != 2:
        new_char = proc.stdout.read(1)

        if new_char == "\n":
            consecutive_newline_count += 1
            if line_buffer.strip():
                original_input, res, *rest = line_buffer.split("\t")
                if "+?" not in rest and "+?" not in res:
                    results.add(res)
            line_buffer = ""
        else:
            line_buffer += new_char
            consecutive_newline_count = 0

    return results
