"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from typing import List, Dict, Tuple, Optional, Set

from colorama import Fore, init
from itertools import chain
import utils
from DatabaseManager.log import DatabaseManagerLogger
from DatabaseManager.xml_consistency_checker import does_lc_match_xml_entry
from constants import Analysis, FSTLemma, SimpleLC
from shared import strict_analyzer

init()  # for windows compatibility


def lemmatize_analyses(
    analysis: Set[str], fst_lemma: FSTLemma, multi_processing: int = 1
):
    """
    use fst to get the lemma-analysis

    :param analysis: fst analysis
    :param fst_lemma: Optimization. Provide fst_lemma to make this function faster. This should be the lemma shown in
        passed in `analysis` argument
    :param multi_processing:
    """
    strict_analyzer.feed_in_bulk_fast([fst_lemma], multi_processing)


def extract_fst_lemmas(
    xml_lemma_to_pos_lc: Dict[str, List[Tuple[str, str]]],
    multi_processing: int = 1,
    verbose=True,
) -> Dict[Tuple[str, str, str], str]:
    """
    For every (xml_lemma, xml_pos, xml_lc), find the its lemma analysis and according to fst file.

    For words that are not nouns and verbs (pronouns, IPCs, ...), no extraction or identification will be done,
    as we don't have the expert rules required to determine their lemmas. res/lemma-tags.tsv is what we rely on.

    Also only noun analysis and verb analysis will appear in the result
    """

    logger = DatabaseManagerLogger(__name__, verbose)
    logger.info("Determining lemma analysis for (xml_lemma, xml_pos, xml_lc) tuples...")

    xml_lemma_pos_lc_to_analysis = dict()  # type: Dict[Tuple[str, str, str], str]

    inflections = xml_lemma_to_pos_lc.keys()

    xml_lemma_to_analyses = strict_analyzer.feed_in_bulk_fast(
        inflections, multi_processing
    )

    fst_lemma_to_analyses: Dict[FSTLemma, Set[Analysis]] = {}

    fst_lemma_to_slc: Dict[FSTLemma, SimpleLC] = {}
    for fst_analysis in chain.from_iterable(xml_lemma_to_analyses.values()):
        x = utils.extract_lemma_and_category(fst_analysis)
        assert x is not None
        fst_lemma_to_slc[x[0]] = x[1]

    no_analysis_counter = 0

    no_match_counter = 0

    other_words_counter = 0  # words that are not verbs or nouns

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
            ]:  # for each pos, lc determine which is the analysis

                # words that are not nouns or verbs
                if (pos != "" and pos not in {"N", "V"}) or (
                    lc != "" and (not lc.startswith("V") and not lc.startswith("N"))
                ):
                    logger.debug(
                        "xml entry %s with pos %s lc %s is neither noun nor verb. No lemma identification carried out"
                        % (xml_lemma, pos, lc)
                    )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    other_words_counter += 1

                # fstLemma and SimpleLC can be extracted from Analysis.
                # It is an optimization here.
                ambiguities: Set[Tuple[Analysis, FSTLemma, SimpleLC]] = set()
                for analysis in analyses:
                    pass

                for (
                    analysis
                ) in (
                    analyses
                ):  # build potential analyses in the loop, ideally len(potential_analyses) == 1
                    lemma_category = utils.extract_lemma_and_category(analysis)
                    assert lemma_category is not None
                    fst_lemma, category = lemma_category
                    assert category is not None
                    if not category.is_noun() and not category.is_verb():
                        continue

                    is_match = does_lc_match_xml_entry(category, pos, lc)
                    if is_match:
                        ambiguities.add((Analysis(analysis), FSTLemma(fst_lemma)))

                if len(ambiguities) == 0:
                    logger.debug(
                        "xml entry %s with pos %s lc %s have analyses by fst strict analyzer. "
                        "None of the analyses are preferred lemma inflection"
                        % (xml_lemma, pos, lc)
                    )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    no_match_counter += 1

                elif len(ambiguities) == 1:  # nice
                    fst_analysis, fst_lemma = ambiguities.pop()
                    # todo: here
                    xml_lemma_pos_lc_to_analysis[
                        xml_lemma, pos, lc
                    ] = lemmatize_analysis(fst_analysis, fst_lemma, multi_processing)
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
        f"{Fore.BLUE}There are %d (lemma, pos, lc) that neither nouns nor verbs. Lemma is not identified for them.{Fore.RESET}"
        % other_words_counter
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
    logger.info("These words will be label 'as-is' without paradigm tables.")

    return xml_lemma_pos_lc_to_analysis
