"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
import csv
import glob
from os import path
from os.path import dirname
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from DatabaseManager.log import DatabaseManagerLogger
from shared import normative_generator
from utils import WordClass, fst_analysis_parser
from utils.paradigm_filler import ParadigmFiller


def expand_inflections(
    analyses: Iterable[str], multi_processing: int = 1, verbose=True
) -> Dict[str, List[Tuple[str, Set[str]]]]:
    """
    for every lemma fst analysis, generate all inflections according to paradigm files
    every analysis in `analyses` should be in the form of a lemma analysis
    """
    logger = DatabaseManagerLogger(__name__, verbose)

    paradigm_filler = ParadigmFiller.default_filler()

    analyses = list(analyses)
    to_generated: Dict[str, List[str]] = {}
    # We'll generate all of the forms for analyses enqueued here in one fell swoop.
    analysis_queue = []

    for analysis in analyses:
        lemma_category = fst_analysis_parser.extract_lemma_text_and_word_class(analysis)
        assert lemma_category is not None
        lemma, category = lemma_category

        if category.has_inflections():
            generated_analyses = list(paradigm_filler.expand_analyses(lemma, category))
        else:
            generated_analyses = [analysis]

        to_generated[analysis] = generated_analyses
        analysis_queue.extend(generated_analyses)

    logger.info("Generating inflections using %d processes..." % multi_processing)

    # optimized for efficiency by calling hfstol once and for all
    generated_analyses_to_inflections = normative_generator.feed_in_bulk_fast(
        analysis_queue, multi_processing
    )

    logger.info("Done generating inflections")

    expanded = {}

    for analysis in analyses:
        pooled_generated_words = []
        for generated_analysis in to_generated[analysis]:
            pooled_generated_words.append(
                (
                    generated_analysis,
                    generated_analyses_to_inflections[generated_analysis],
                )
            )
        expanded[analysis] = pooled_generated_words
    return expanded
