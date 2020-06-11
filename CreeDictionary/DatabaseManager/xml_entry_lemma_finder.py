"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from collections import defaultdict
from itertools import chain
from string import Template
from typing import List, Dict, Tuple, Set, Optional, Any

from colorama import Fore, init
from typing_extensions import Literal

import utils
from DatabaseManager.log import DatabaseManagerLogger
from DatabaseManager.xml_consistency_checker import does_lc_match_xml_entry
from utils.types import FSTLemma, ConcatAnalysis
from utils import WC
from shared import strict_analyzer
from utils import shared_res_dir, ConcatAnalysis, FSTLemma
import csv

init()  # for windows compatibility


class DefaultLemmaPicker:
    """
    When two analyses have the same looking lemma and word class, this helps choose the preferred lemma

    i.e. It helps solve this question: "Which one of maskwa+N+A+Sg and maskwa+N+A+Obv is the lemma?"
    """

    def __init__(self, language: Literal["crk", "srs"]):

        self._word_class_to_lemma_analysis_templates: Dict[
            SimpleLC, List[Template]
        ] = {}

        lemma_tags_path = shared_res_dir / "lemma_tags" / language / "lemma-tags.tsv"

        with open(lemma_tags_path) as lemma_tags_file:
            for row in csv.reader(lemma_tags_file, delimiter="\t"):
                str_word_class, templates = row
                self._word_class_to_lemma_analysis_templates[
                    SimpleLC(str_word_class.strip().upper())
                ] = [Template(t) for t in templates.strip().split(" ")]

    def get_lemma(self, ambiguities: Set[ConcatAnalysis]) -> Optional[ConcatAnalysis]:
        """
        Pick the lemma analysis according to the looks of the usual lemma analyses for each word class.
        """
        for ambiguity in ambiguities:
            lemma_wc = utils.fst_analysis_parser.extract_lemma_and_category(ambiguity)
            assert lemma_wc is not None
            lemma, word_class = lemma_wc

            templates = self._word_class_to_lemma_analysis_templates.get(word_class)
            if templates is None:
                return None

            if ambiguity in {t.substitute(lemma=lemma) for t in templates}:
                return ambiguity
        return None


crk_default_lemma_picker = DefaultLemmaPicker(language="crk")


def extract_fst_lemmas(
    xml_lemma_to_pos_lc: Dict[str, List[Tuple[str, str]]],
    multi_processing: int = 1,
    verbose=True,
) -> Dict[Tuple[str, str, str], ConcatAnalysis]:
    """
    For every (xml_lemma, xml_pos, xml_lc), try to find its lemma analysis and according to fst. Analysis may be empty
    string if the lemma analysis can't be decided
    """

    logger = DatabaseManagerLogger(__name__, verbose)
    logger.info("Determining lemma analysis for (xml_lemma, xml_pos, xml_lc) tuples...")

    xml_lemma_pos_lc_to_analysis = (
        dict()
    )  # type: Dict[Tuple[str, str, str], ConcatAnalysis]

    inflections = xml_lemma_to_pos_lc.keys()

    xml_lemma_to_analyses = strict_analyzer.feed_in_bulk_fast(
        inflections, multi_processing
    )

    produced_extra_lemmas: List[FSTLemma] = []

    fst_analysis_to_fst_lemma_slc: Dict[
        ConcatAnalysis, Tuple[FSTLemma, WC]
    ] = dict()
    for fst_analysis in chain.from_iterable(xml_lemma_to_analyses.values()):
        x = utils.extract_lemma_and_category(fst_analysis)
        assert x is not None
        produced_lemma, slc = x
        fst_analysis_to_fst_lemma_slc[fst_analysis] = produced_lemma, slc
        if produced_lemma not in xml_lemma_to_analyses:
            produced_extra_lemmas.append(produced_lemma)

    produced_extra_lemma_to_analysis: Dict[
        FSTLemma, Set[ConcatAnalysis]
    ] = strict_analyzer.feed_in_bulk_fast(produced_extra_lemmas)

    for fst_analysis in chain.from_iterable(produced_extra_lemma_to_analysis.values()):
        x = utils.extract_lemma_and_category(fst_analysis)
        assert x is not None
        produced_lemma, slc = x
        fst_analysis_to_fst_lemma_slc[fst_analysis] = produced_lemma, slc

    all_lemma_to_analysis = xml_lemma_to_analyses.copy()
    all_lemma_to_analysis.update(produced_extra_lemma_to_analysis)

    no_analysis_counter = 0

    no_match_counter = 0

    success_counter = 0
    dup_counter = 0

    for xml_lemma, analyses in xml_lemma_to_analyses.items():

        if len(analyses) == 0:

            if xml_lemma in xml_lemma_to_pos_lc:
                for pos, lc in xml_lemma_to_pos_lc[xml_lemma]:
                    xml_lemma_pos_lc_to_analysis[(xml_lemma, pos, lc)] = ConcatAnalysis(
                        ""
                    )
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

            possible_lemma_analyses: List[ConcatAnalysis] = []
            for analysis in analyses:
                fst_lemma, slc = fst_analysis_to_fst_lemma_slc[analysis]
                fst_lemma_analyses = all_lemma_to_analysis[fst_lemma]

                for fst_lemma_analysis in fst_lemma_analyses:
                    x = utils.extract_lemma_and_category(fst_lemma_analysis)
                    assert x is not None
                    wordform, slc = x
                    if slc is slc and wordform == fst_lemma:
                        possible_lemma_analyses.append(fst_lemma_analysis)

            for pos, lc in xml_lemma_to_pos_lc[
                xml_lemma
            ]:  # for each pos, lc determine which is the analysis

                ambiguities: Set[ConcatAnalysis] = set()

                # put priority in looking for a unique and identical wordform
                # this principle is used in the hope that it will help with lemma resolution
                # of diminutive nouns.
                # see: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
                # Otherwise a lot of diminutive nouns will have no analysis
                wordform_to_ambiguous_analyses: Dict[
                    FSTLemma, Set[ConcatAnalysis]
                ] = defaultdict(set)

                for (
                    analysis
                ) in (
                    possible_lemma_analyses
                ):  # build potential analyses in the loop, ideally len(potential_analyses) == 1
                    fst_lemma, slc = fst_analysis_to_fst_lemma_slc[analysis]

                    is_match = does_lc_match_xml_entry(slc, pos, lc)
                    if is_match:
                        ambiguities.add(analysis)
                        wordform_to_ambiguous_analyses[fst_lemma].add(analysis)

                # there's only one identically matching wordform, just use that one
                for (
                    wordform,
                    ambiguous_analyses,
                ) in wordform_to_ambiguous_analyses.items():
                    if wordform == xml_lemma and len(ambiguous_analyses) == 1:
                        ambiguities = ambiguous_analyses
                        break

                if len(ambiguities) == 0:
                    logger.debug(
                        "xml entry %s with pos %s lc %s have analyses by fst strict analyzer. "
                        "Yet all analyses conflict with the pos/lc in xml file"
                        % (xml_lemma, pos, lc)
                    )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ConcatAnalysis(
                        ""
                    )
                    no_match_counter += 1

                elif len(ambiguities) == 1:  # nice
                    fst_analysis = ambiguities.pop()
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ConcatAnalysis(
                        fst_analysis
                    )
                    success_counter += 1
                else:
                    # check if it contains default forms of lemma analyses
                    res = crk_default_lemma_picker.get_lemma(ambiguities)
                    if res is not None:
                        xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = res
                        success_counter += 1
                    else:
                        logger.debug(
                            "xml entry %s with pos %s lc %s have more "
                            "than one potential analyses by fst strict analyzer."
                            % (xml_lemma, pos, lc)
                        )
                        xml_lemma_pos_lc_to_analysis[
                            xml_lemma, pos, lc
                        ] = ConcatAnalysis("")
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
        "These words will be label 'as-is', meaning their lemmas are undetermined."
    )

    return xml_lemma_pos_lc_to_analysis
