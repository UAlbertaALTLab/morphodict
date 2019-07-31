import shutil
import subprocess
from os import path
from typing import Iterable

HFSTOL_PATH = shutil.which("hfst-optimized-lookup")
FILE_DIR = path.dirname(__file__)

if HFSTOL_PATH is None:
    raise ImportError(
        "hfst-optimized-lookup is not installed.\n"
        "Please install the HFST suite on your system "
        "before importing this module.\n"
        "See: https://github.com/hfst/hfst#installation"
    )


def analyze_in_bulk(surface_forms: Iterable[str]):
    """
    use hfstol to do word analysis in bulk. May have two orders of magnitude of performance gain compared to
    invoking analyze() for every word.

    Note: The returned analyses are formatted different than analyze().
    """

    # hfst-optimized-lookup expects each analysis on a separate line:
    lines = "\n".join(surface_forms).encode("UTF-8")

    status = subprocess.run(
        [
            HFSTOL_PATH,
            "--verbose",
            "--pipe-mode",
            path.join(FILE_DIR, "..", "res", "fst", "crk-descriptive-analyzer.hfstol"),
        ],
        input=lines,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )

    analyses = []

    old_surface_form = None
    for line in status.stdout.decode("UTF-8").splitlines():
        print(line)
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
        surface_form, word_form, *rest = line.split("\t")

        if old_surface_form is None:
            analyses.append([])
        else:
            if surface_form != old_surface_form:
                analyses.append([])
        old_surface_form = surface_form
        # Generating this word form failed!
        if "+?" in rest:
            analyses[-1].append("")
        else:
            analyses[-1].append(word_form)
            analyses[-1].append(surface_form)

    return analyses
