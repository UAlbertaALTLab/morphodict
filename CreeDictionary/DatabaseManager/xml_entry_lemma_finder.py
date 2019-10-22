"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from os.path import dirname
from pathlib import Path
from typing import List, Dict, Tuple

from colorama import Fore, init
from hfstol import HFSTOL

import utils
from DatabaseManager.log import DatabaseManagerLogger
from DatabaseManager.xml_consistency_checker import does_hfstol_xml_pos_match
from utils import fst_analysis_parser
from shared import strict_analyzer

init()  # for windows compatibility


def extract_fst_lemmas(
    xml_lemma_to_pos_lc: Dict[str, List[Tuple[str, str]]],
    multi_processing: int = 1,
    verbose=True,
) -> Dict[Tuple[str, str, str], str]:
    """
    for every (xml_lemma, pos, lc), find the analysis of its lemma and according to fst.
    """

    logger = DatabaseManagerLogger(__name__, verbose)

    logger.info("Determining lemma analysis for (xml_lemma, pos, lc) tuples...")

    xml_lemma_pos_lc_to_analysis = dict()  # type: Dict[Tuple[str, str, str], str]

    # xml_lemma_to_analyses_inflections = (
    #     dict()
    # )  # type: Dict[str, List[Tuple[str,List[str]]]]

    inflections = xml_lemma_to_pos_lc.keys()

    xml_lemma_to_analyses = strict_analyzer.feed_in_bulk_fast(
        inflections, multi_processing
    )

    no_analysis_counter = 0

    no_match_counter = 0
    success_counter = 0
    dup_counter = 0

    for xml_lemma, analyses in xml_lemma_to_analyses.items():

        if len(analyses) == 0:

            if xml_lemma in xml_lemma_to_pos_lc:
                for pos, lc in xml_lemma_to_pos_lc[xml_lemma]:
                    xml_lemma_pos_lc_to_analysis[(xml_lemma, pos, lc)] = ""
                    logger.debug(
                        "xml entry %s with pos %s lc %s can not be analyzed by fst strict analyzer"
                        % (xml_lemma, pos, lc)
                    )
                    no_analysis_counter += 1

        else:

            # possible pos
            # {'', 'IPV', 'Pron', 'N', 'Ipc', 'V', '-'}

            # possible lc
            # {'', 'NDA-1', 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
            # 'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
            # 'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
            # 'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
            # 'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}

            for pos, lc in xml_lemma_to_pos_lc[
                xml_lemma
            ]:  # determine which is `the` analysis

                ambiguous_analyses = set()

                hfstol_lemma_analyses = hfstol_analysis_parser.identify_lemma_analysis(
                    analyses
                )

                for (
                    analysis
                ) in (
                    hfstol_lemma_analyses
                ):  # build potential analyses in the loop, ideally len(potential_analyses) == 1
                    category = utils.extract_category(analysis)
                    assert category is not None

                    is_match = does_hfstol_xml_pos_match(category, pos, lc)
                    if is_match:
                        ambiguous_analyses.add(analysis)

                if len(ambiguous_analyses) == 0:
                    logger.debug(
                        "xml entry %s with pos %s lc %s have analyses by fst strict analyzer. None of the analyses are preferred lemma inflection"
                        % (xml_lemma, pos, lc)
                    )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    no_match_counter += 1

                elif len(ambiguous_analyses) == 1:  # nice
                    the_analysis = ambiguous_analyses.pop()
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = the_analysis
                    success_counter += 1
                else:
                    logger.debug(
                        "xml entry %s with pos %s lc %s have more than one potential analyses by fst strict analyzer."
                        % (xml_lemma, pos, lc)
                    )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    dup_counter += 1

    logger.info(
        f"{Fore.GREEN}%d (lemma, pos, lc) found proper lemma analysis{Fore.RESET}"
        % success_counter
    )
    logger.info(
        f"{Fore.BLUE}There are %d (lemma, pos, lc) that the fst can not give any analyses.{Fore.RESET}"
        % no_analysis_counter
    )
    logger.info(
        f"{Fore.BLUE}There are %d (lemma, pos, lc) that do not have proper lemma analysis by fst{Fore.RESET}"
        % no_match_counter
    )

    logger.info(
        f"{Fore.BLUE}There are %d (lemma, pos, lc) that have ambiguous lemma analyses{Fore.RESET}"
        % dup_counter
    )
    logger.info(
        "These words will be shown 'as-is' without analyses and paradigm tables"
    )

    return xml_lemma_pos_lc_to_analysis
