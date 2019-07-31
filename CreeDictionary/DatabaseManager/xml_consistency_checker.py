"""check the consistency of a xml source with a fst"""
from os.path import dirname
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Set

from hfstol import HFSTOL

import utils
from utils import hfstol_analysis_parser
from constants import PathLike, InflectionCategory
import xml.etree.ElementTree as ET


descriptive_analyzer_file = (
    Path(dirname(__file__)) / ".." / "res" / "fst" / "crk-descriptive-analyzer.hfstol"
)
strict_analyzer_file = (
    Path(dirname(__file__)) / ".." / "res" / "fst" / "crk-strict-analyzer.hfstol"
)

descriptive_analyzer = HFSTOL.from_file(descriptive_analyzer_file)
strict_analyzer = HFSTOL.from_file(strict_analyzer_file)


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


def does_hfstol_xml_pos_match(
    hfstol_category: InflectionCategory, xml_pos: str, xml_lc: str
):

    if (
        (xml_pos == "V" and hfstol_category.is_verb())
        or (xml_pos == "N" and hfstol_category.is_noun())
        or (xml_pos == "Ipc" and hfstol_category is InflectionCategory.IPC)
        or (xml_pos == "Pron" and hfstol_category is InflectionCategory.Pron)
    ):
        lc_category = parse_xml_lc(xml_lc)

        if lc_category is None or hfstol_category is lc_category:
            return True
        else:
            return False
    else:
        return False


def check_xml(filename: PathLike, verbose, check_only: Optional[str]):
    root = ET.parse(filename).getroot()
    # there are entries that look the same, thus `List`[...]
    xml_lemma_to_pos_lc = dict()  # type: Dict[str, List[Tuple[str,str]]]
    elements = root.findall(".//e")

    xml_lemma_pos_lc = set()
    counter = 0
    for element in elements:
        l = element.find("lg/l")
        lc_str = element.find("lg/lc").text
        xml_lemma, pos_str = l.text, l.get("pos")
        xml_lemma_pos_lc.add((xml_lemma, pos_str, lc_str))
        if xml_lemma in xml_lemma_to_pos_lc:
            xml_lemma_to_pos_lc[xml_lemma].append((pos_str, lc_str))
        else:
            xml_lemma_to_pos_lc[xml_lemma] = [(pos_str, lc_str)]
        counter += 1

    inflections = xml_lemma_to_pos_lc.keys()
    print(len(xml_lemma_to_pos_lc))
    strict_xml_lemma_to_analyses = strict_analyzer.feed_in_bulk_fast(inflections)
    # descriptive_xml_lemma_to_analyses = descriptive_analyzer.feed_in_bulk_fast(
    #     inflections
    # )

    lemmas_wo_analysis = set()

    inconsistent_xml_pos_lc = set()

    ambiguous_xml_pos_lc_to_analyses_lemmas = (
        dict()
    )  # type: Dict[Tuple[str, str, str], Tuple[Set[str], Set[str]]]

    dup_counter = 0

    pos_set = set()
    for xml_lemma, analyses in strict_xml_lemma_to_analyses.items():

        if len(analyses) == 0:
            lemmas_wo_analysis.add(xml_lemma)
        elif len(analyses) >= 1:  # determine which is `the` analysis

            # possible pos
            # {'', 'IPV', 'Pron', 'N', 'Ipc', 'V', '-'}

            # possible lc
            # {'NDA-1', None, 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
            # 'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
            # 'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
            # 'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
            # 'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}

            for pos, lc in xml_lemma_to_pos_lc[xml_lemma]:

                ambiguous_analyses = set()
                ambiguous_lemmas = set()
                lemma_analyses = hfstol_analysis_parser.identify_lemma_analysis(
                    analyses
                )

                for (
                    analysis
                ) in (
                    lemma_analyses
                ):  # build potential analyses in the loop, ideally len(potential_analyses) == 1

                    category = utils.extract_category(analysis)
                    assert category is not None
                    is_match = does_hfstol_xml_pos_match(category, pos, lc)

                    if is_match:
                        analysis_lemma = hfstol_analysis_parser.extract_lemma(analysis)
                        ambiguous_lemmas.add(analysis_lemma)
                        ambiguous_analyses.add(analysis)

                if len(ambiguous_analyses) == 0:

                    inconsistent_xml_pos_lc.add((xml_lemma, pos, lc))

                elif len(ambiguous_analyses) == 1:  # nice
                    pass
                else:
                    ambiguous_xml_pos_lc_to_analyses_lemmas[(xml_lemma, pos, lc)] = (
                        ambiguous_analyses,
                        ambiguous_lemmas,
                    )

    rere = descriptive_analyzer.feed_in_bulk_fast(lemmas_wo_analysis)
    saved = 0
    for l in lemmas_wo_analysis:
        if rere[l]:
            saved += 1

    check_name_to_summary_results = dict()  # type: Dict[str, Tuple[str, str]]

    ambiguity_res = "Ambiguous xml entries:\n"
    if len(ambiguous_xml_pos_lc_to_analyses_lemmas) >= 10 and not verbose:
        sample_size = 5
    else:
        sample_size = len(ambiguous_xml_pos_lc_to_analyses_lemmas)

    for (lemma, pos, lc), (analyses, lemmas) in list(
        ambiguous_xml_pos_lc_to_analyses_lemmas.items()
    )[:sample_size]:
        ambiguity_res += "xml: %s\tpos: %s\tlc: %s\n" % (lemma, pos, lc)
        # ambiguity_res += "fst output: %s\n" % strict_xml_lemma_to_analyses[lemma]
        ambiguity_res += "which is the preferred lemma: %s\n" % analyses
        if len(lemmas) > 1:
            ambiguity_res += "which is the actually lemma: %s\n" % lemmas
        ambiguity_res += "\n"

    if sample_size < len(ambiguous_xml_pos_lc_to_analyses_lemmas):
        ambiguity_res += "...[the rest %d items omitted]\n\n" % (
            len(ambiguous_xml_pos_lc_to_analyses_lemmas) - 5
        )
    ambiguity_summary = (
        "Can't determine the lemma for %d entries in crkeng.xml\n"
        % len(ambiguous_xml_pos_lc_to_analyses_lemmas)
    )

    check_name_to_summary_results["ambiguity"] = (ambiguity_summary, ambiguity_res)

    if check_only == "ambiguity":
        name = "ambiguity_check"
    else:
        name = "inconsistency"

    if verbose:
        name += "_verbose"

    name += ".txt"

    with open(name, "w") as file:
        summaries = []
        details = []

        for summary, detail in check_name_to_summary_results.values():
            summaries.append(summary)
            details.append(detail)

        for summary in summaries:
            file.write(summary)
        file.write("\n")
        for detail in details:
            file.write(detail)

        # file.write("Summary:\n")
        # file.write("There are %d entries in crkeng.xml in total\n" % (counter))
        # file.write(
        #     "There are %d entries in crkeng.xml that crk-strict-analyzer.hfstol can not give any analyses. %d out of them can be recognized by descriptive analyzers and may be caused by spelling issues\n"
        #     % (len(lemmas_wo_analysis), saved)
        # )
        #
        # file.write(
        #     "There are %d entries in crkeng.xml that has 'pos' and <lc> not consistent with any analysis given by crk-strict-analyzer.hfstol\n"
        #     % len(inconsistent_xml_pos_lc)
        # )
        # file.write()
        #
        # file.write("\n\n")
        #
        # file.write("Entries with no analysis:\n")
        #
        # if len(lemmas_wo_analysis) >= 10 and not verbose:
        #     for l in list(lemmas_wo_analysis)[:5]:
        #         file.write(l + "\n")
        #     file.write(
        #         "...[the rest %d items omitted]\n" % (len(lemmas_wo_analysis) - 5)
        #     )
        # else:
        #     for l in lemmas_wo_analysis:
        #         file.write(l + "\n")
        #
        # file.write("\n\n")
        #
        # file.write("Entries with inconsistent analysis:\n")
        #
        # if len(inconsistent_xml_pos_lc) >= 10 and not verbose:
        #     for lemma, pos, lc in list(inconsistent_xml_pos_lc)[:5]:
        #         file.write("xml: %s\tpos: %s\tlc: %s\n" % (lemma, pos, lc))
        #         file.write("fst: %s\n" % strict_xml_lemma_to_analyses[lemma])
        #         file.write("\n")
        #     file.write(
        #         "...[the rest %d items omitted]\n\n"
        #         % (len(inconsistent_xml_pos_lc) - 5)
        #     )
        # else:
        #     for lemma, pos, lc in inconsistent_xml_pos_lc:
        #         file.write("xml: %s\tpos: %s\tlc: %s\n\n" % (lemma, pos, lc))
        #         file.write("fst: %s\n" % strict_xml_lemma_to_analyses[lemma])
        #         file.write("\n")
