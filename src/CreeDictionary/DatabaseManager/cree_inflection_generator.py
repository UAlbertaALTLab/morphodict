"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from typing import Dict, Iterable, List, Set, Tuple

import morphodict.analysis
from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.CreeDictionary.views import (
    convert_crkeng_word_class_to_paradigm_name,
)
from CreeDictionary.DatabaseManager.log import DatabaseManagerLogger
from CreeDictionary.utils import WordClass, fst_analysis_parser


def expand_inflections(
    analyses: Iterable[str], verbose=True
) -> Dict[str, List[Tuple[str, Set[str]]]]:
    """
    for every lemma fst analysis, generate all inflections according to paradigm files
    every analysis in `analyses` should be in the form of a lemma analysis
    """
    logger = DatabaseManagerLogger(__name__, verbose)

    paradigm_manager = default_paradigm_manager()

    analyses = list(analyses)
    to_generated: Dict[str, List[str]] = {}
    # We'll generate all of the forms for analyses enqueued here in one fell swoop.
    analysis_queue: list[str] = []

    for analysis in analyses:
        lemma, word_class = lemma_and_wordclass_from_analysis(analysis)

        if word_class.has_inflections():
            paradigm_name = convert_crkeng_word_class_to_paradigm_name(word_class)
            generated_analyses = list(
                paradigm_manager.all_analyses(paradigm_name, lemma)
            )
        else:
            generated_analyses = [analysis]

        to_generated[analysis] = generated_analyses
        analysis_queue.extend(generated_analyses)

    logger.info("Generating inflections ...")

    generated_analyses_to_inflections = (
        morphodict.analysis.strict_generator().bulk_lookup(analysis_queue)
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


def lemma_and_wordclass_from_analysis(analysis: str) -> tuple[str, WordClass]:
    result = fst_analysis_parser.extract_lemma_text_and_word_class(analysis)
    assert result is not None, "expand_inflections should all have valid analyses!"
    return result
