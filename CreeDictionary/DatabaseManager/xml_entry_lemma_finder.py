"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""
from colorama import Fore
from os.path import dirname
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from hfstol import HFSTOL

import utils
from DatabaseManager.xml_consistency_checker import does_hfstol_xml_pos_match
from constants import InflectionCategory

# analyzer_file = (
#     Path(dirname(__file__)) / ".." / "res" / "fst" / "crk-descriptive-analyzer.hfstol"
# )
from utils import hfstol_analysis_parser

analyzer_file = (
    Path(dirname(__file__)) / ".." / "res" / "fst" / "crk-strict-analyzer.hfstol"
)

analyzer = HFSTOL.from_file(analyzer_file)


def parse_xml_lc(lc_text: str) -> Optional[InflectionCategory]:
    """
    return recognized lc
    :param lc_text: 2019 July, all lc from crkeng.xml are
        {'NDA-1', None, 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
        'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
        'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
        'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
        'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}
    :return:
    """
    if lc_text is None:
        return None
    if lc_text.startswith("VTA"):
        return InflectionCategory.VTA
    if lc_text.startswith("VTI"):
        return InflectionCategory.VTI
    if lc_text.startswith("VAI"):
        return InflectionCategory.VAI
    if lc_text.startswith("VII"):
        return InflectionCategory.VII
    if lc_text.startswith("NDA"):
        return InflectionCategory.NAD
    if lc_text.startswith("NI"):
        return InflectionCategory.NI
    if lc_text.startswith("NDI"):
        return InflectionCategory.NID
    if lc_text.startswith("NA"):
        return InflectionCategory.NA

    if lc_text.startswith("IPC"):
        return InflectionCategory.IPC

    return None


def parse_xml_pos(pos: str) -> str:
    pass


def extract_fst_lemmas(
    xml_lemma_to_pos_lc: Dict[str, List[Tuple[str, str]]], multi_processing: int = 1
) -> Dict[Tuple[str, str, str], str]:
    """
    for every (xml_lemma, pos, lc), find the analysis of its lemma and according to fst.
    """

    print("Determining lemma analysis for (xml_lemma, pos, lc) tuples...")

    xml_lemma_pos_lc_to_analysis = dict()  # type: Dict[Tuple[str, str, str], str]

    # xml_lemma_to_analyses_inflections = (
    #     dict()
    # )  # type: Dict[str, List[Tuple[str,List[str]]]]

    inflections = xml_lemma_to_pos_lc.keys()

    xml_lemma_to_analyses = analyzer.feed_in_bulk_fast(inflections, multi_processing)

    no_analysis_counter = 0

    no_match_counter = 0
    success_counter = 0
    dup_counter = 0

    for xml_lemma, analyses in xml_lemma_to_analyses.items():

        if len(analyses) == 0:

            if xml_lemma in xml_lemma_to_pos_lc:
                for pos, lc in xml_lemma_to_pos_lc[xml_lemma]:
                    xml_lemma_pos_lc_to_analysis[(xml_lemma, pos, lc)] = ""
                    # print(
                    #     "xml entry %s with pos %s lc %s can not be analyzed by fst strict analyzer"
                    #     % (xml_lemma, pos, lc)
                    # )
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
                    # print(
                    #     "xml entry %s with pos %s lc %s have analyses by fst strict analyzer. None of the analyses are preferred lemma inflection"
                    #     % (xml_lemma, pos, lc)
                    # )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    no_match_counter += 1

                elif len(ambiguous_analyses) == 1:  # nice
                    the_analysis = ambiguous_analyses.pop()
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = the_analysis
                    success_counter += 1
                else:
                    # print(
                    #     "xml entry %s with pos %s lc %s have more than one potential analyses by fst strict analyzer."
                    #     % (xml_lemma, pos, lc)
                    # )
                    xml_lemma_pos_lc_to_analysis[xml_lemma, pos, lc] = ""
                    dup_counter += 1
    print(Fore.GREEN)
    print("%d (lemma, pos, lc) found proper lemma analysis" % success_counter)
    print(Fore.BLUE)
    print(
        "There are %d (lemma, pos, lc) that the fst can not give any analyses."
        % no_analysis_counter
    )
    print(
        "There are %d (lemma, pos, lc) that do not have proper lemma analysis by fst"
        % no_match_counter
    )

    print(
        "There are %d (lemma, pos, lc) that have ambiguous lemma analyses" % dup_counter
    )
    print("These words will be shown 'as-is' without analyses and paradigm tables")

    print(Fore.RESET)

    return xml_lemma_pos_lc_to_analysis
