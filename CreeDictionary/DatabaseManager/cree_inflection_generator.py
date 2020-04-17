"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
import csv
import glob
from os import path
from os.path import dirname
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from constants import SimpleLexicalCategory
from DatabaseManager.log import DatabaseManagerLogger
from shared import normative_generator
from utils import fst_analysis_parser


def import_flattened_prefilled_layouts(
    layout_file_dir: Path,
) -> Dict[SimpleLexicalCategory, List[str]]:
    """
    >>> import_flattened_prefilled_layouts(Path(dirname(__file__)) / '..' / 'res' / 'prefilled_layouts')[SimpleLexicalCategory.NID]
    ['{{ lemma }}+N+I+D+PxX+Sg', '{{ lemma }}+N+I+D+PxX+Pl', '{{ lemma }}+N+I+D+PxX+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+PxX+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+PxX+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+PxX+Loc', '{{ lemma }}+N+I+D+Px1Sg+Sg', '{{ lemma }}+N+I+D+Px1Sg+Pl', '{{ lemma }}+N+I+D+Px1Sg+Loc', '{{ lemma }}+N+I+D+Px2Sg+Sg', '{{ lemma }}+N+I+D+Px2Sg+Pl', '{{ lemma }}+N+I+D+Px2Sg+Loc', '{{ lemma }}+N+I+D+Px3Sg+Sg', '{{ lemma }}+N+I+D+Px3Sg+Pl', '{{ lemma }}+N+I+D+Px3Sg+Loc', '{{ lemma }}+N+I+D+Px1Pl+Sg', '{{ lemma }}+N+I+D+Px1Pl+Pl', '{{ lemma }}+N+I+D+Px1Pl+Loc', '{{ lemma }}+N+I+D+Px12Pl+Sg', '{{ lemma }}+N+I+D+Px12Pl+Pl', '{{ lemma }}+N+I+D+Px12Pl+Loc', '{{ lemma }}+N+I+D+Px2Pl+Sg', '{{ lemma }}+N+I+D+Px2Pl+Pl', '{{ lemma }}+N+I+D+Px2Pl+Loc', '{{ lemma }}+N+I+D+Px3Pl+Sg', '{{ lemma }}+N+I+D+Px3Pl+Pl', '{{ lemma }}+N+I+D+Px3Pl+Loc', '{{ lemma }}+N+I+D+Px4Sg/Pl+Sg', '{{ lemma }}+N+I+D+Px4Sg/Pl+Pl', '{{ lemma }}+N+I+D+Px4Sg/Pl+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Sg+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Sg+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Sg+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Sg+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Sg+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Sg+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Sg+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Sg+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Sg+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Pl+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Pl+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px1Pl+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px12Pl+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px12Pl+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px12Pl+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Pl+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Pl+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px2Pl+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Pl+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Pl+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px3Pl+Loc', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px4Sg/Pl+Sg', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px4Sg/Pl+Pl', '{{ lemma }}+N+I+D+Der/Dim+N+I+D+Px4Sg/Pl+Loc']
    """
    flattened_layouts = dict()
    files = glob.glob(str(layout_file_dir / "*-linguistic*.tsv"))
    for file in files:

        name_wo_extension = str(path.split(file)[1]).split(".")[0]

        with open(file, "r") as f:

            reader = csv.reader(f, delimiter="\t", quotechar="'")
            flattened_layout = [
                cell for row in reader for cell in row if '"' not in cell and cell != ""
            ]
            ic_str, size_str = name_wo_extension.split("-")
            flattened_layouts[SimpleLexicalCategory(ic_str.upper())] = flattened_layout
    return flattened_layouts


def expand_inflections(
    analyses: Iterable[str], multi_processing: int = 1, verbose=True
) -> Dict[str, List[Tuple[str, Set[str]]]]:
    """
    for every lemma fst analysis, generate all inflections according to paradigm files
    every analysis in `analyses` should be in the form of a lemma analysis
    """
    logger = DatabaseManagerLogger(__name__, verbose)

    # optimized for efficiency by calling hfstol once and for all
    flattened_layouts = import_flattened_prefilled_layouts(
        Path(dirname(__file__)) / ".." / "res" / "prefilled_layouts"
    )
    fat_generated_analyses = []

    analyses = list(analyses)

    to_generated = dict()  # type: Dict[str, List[str]]

    for analysis in analyses:
        lemma_category = fst_analysis_parser.extract_lemma_and_category(analysis)
        assert lemma_category is not None
        lemma, category = lemma_category
        if category.is_verb() or category.is_noun():
            generated_analyses = [
                generated_analysis.replace("{{ lemma }}", lemma)
                for generated_analysis in flattened_layouts[category]
            ]
        else:
            generated_analyses = [analysis]
        to_generated[analysis] = generated_analyses
        fat_generated_analyses.extend(generated_analyses)

    logger.info("Generating inflections using %d processes..." % multi_processing)
    generated_analyses_to_inflections = normative_generator.feed_in_bulk_fast(
        fat_generated_analyses, multi_processing
    )

    logger.info("Done generating inflections")

    expanded = dict()

    for analysis in analyses:
        pooled_generated_words = list()
        for generated_analysis in to_generated[analysis]:
            pooled_generated_words.append(
                (
                    generated_analysis,
                    generated_analyses_to_inflections[generated_analysis],
                )
            )
        expanded[analysis] = pooled_generated_words
    return expanded
