"""
EXPAND lemma with inflections from xml according to an fst and paradigm/layout files
"""

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from itertools import chain
from pathlib import Path
from string import Template
from typing import Dict, Iterable, List, Optional, Set, Tuple, cast, Sequence

from colorama import Fore, init
from typing_extensions import Literal

from CreeDictionary.DatabaseManager.log import DatabaseManagerLogger
from CreeDictionary.DatabaseManager.xml_consistency_checker import (
    does_inflectional_category_match_xml_entry,
)
from CreeDictionary.shared import expensive
from CreeDictionary.utils import WordClass, shared_res_dir, fst_analysis_parser
from CreeDictionary.utils.crkeng_xml_utils import IndexedXML
from CreeDictionary.utils.data_classes import XMLEntry
from CreeDictionary.utils.types import ConcatAnalysis, FSTLemma

init()  # for windows compatibility


class DefaultLemmaPicker:
    """
    When two analyses have the same looking lemma and word class, this helps choose the preferred lemma

    i.e. It helps solve this question: "Which one of maskwa+N+A+Sg and maskwa+N+A+Obv is the lemma?"
    """

    def __init__(self, language: Literal["crk", "srs"]):

        self._word_class_to_lemma_analysis_templates: Dict[
            WordClass, List[Template]
        ] = {}

        lemma_tags_path = shared_res_dir / "lemma_tags" / language / "lemma-tags.tsv"

        with open(lemma_tags_path) as lemma_tags_file:
            for row in csv.reader(lemma_tags_file, delimiter="\t"):
                str_word_class, templates = row
                self._word_class_to_lemma_analysis_templates[
                    WordClass(str_word_class.strip().upper())
                ] = [Template(t) for t in templates.strip().split(" ")]

    def get_lemma(self, ambiguities: Set[ConcatAnalysis]) -> Optional[ConcatAnalysis]:
        """
        Pick the lemma analysis according to the looks of the usual lemma analyses for each word class.
        """
        for ambiguity in ambiguities:
            lemma_wc = fst_analysis_parser.extract_lemma_text_and_word_class(ambiguity)
            assert lemma_wc is not None
            lemma, word_class = lemma_wc

            templates = self._word_class_to_lemma_analysis_templates.get(word_class)
            if templates is None:
                return None

            if ambiguity in {t.substitute(lemma=lemma) for t in templates}:
                return ambiguity
        return None


crk_default_lemma_picker = DefaultLemmaPicker(language="crk")


@dataclass
class ImportInconsistency:
    xml_entry: XMLEntry
    reason: str
    analyses: Sequence[ConcatAnalysis] = ()


class InconsistencyCollection:
    def __init__(self):
        self._inconsistencies: list[ImportInconsistency] = []

    def add(self, inconsistency: ImportInconsistency):
        self._inconsistencies.append(inconsistency)

    def write_to_disk(self, path_without_extension: Path) -> Path:
        """
        Write the collected inconsistencies to disk, returning the list of saved paths.
        """
        outfile = path_without_extension.with_suffix(".jsonl")
        with open(outfile, "w") as f:
            for i in self._inconsistencies:
                f.write(json.dumps(asdict(i), ensure_ascii=False) + "\n")
        return outfile


def identify_entries(
    crkeng_xml: IndexedXML,
    write_out_inconsistencies=False,
    verbose=True,
) -> Tuple[Dict[XMLEntry, ConcatAnalysis], List[XMLEntry]]:
    """
    For every entry in the XML file, try to find its lemma analysis according to the FST.

    :returns: Entries with their lemma analyses. And "as is" entries that we fail to provide a lemma analysis,
        either because the FST doesn't recognize the entry or there are ambiguities.
    """

    def get_all_ls() -> Iterable[str]:
        ls = crkeng_xml.values_list("l", flat=True)
        assert all(isinstance(l, str) for l in ls)  # type: ignore
        return cast(Iterable[str], ls)

    logger = DatabaseManagerLogger(__name__, verbose)
    logger.info("Determining lemma analysis for entries...")

    # The first return value. Each entry to their lemma analysis
    entry_to_analysis = dict()  # type: Dict[XMLEntry, ConcatAnalysis]
    # The second return value. Lemmas that we fail to provide a lemma analysis
    as_is_entries = []

    ls = get_all_ls()
    l_to_analyses = cast(
        Dict[FSTLemma, Set[ConcatAnalysis]],
        expensive.strict_analyzer.bulk_lookup(ls),
    )

    produced_extra_lemmas: List[FSTLemma] = []

    fst_analysis_to_fst_lemma_wc: Dict[ConcatAnalysis, Tuple[FSTLemma, WordClass]] = {}
    for fst_analysis in chain.from_iterable(l_to_analyses.values()):
        x = fst_analysis_parser.extract_lemma_text_and_word_class(fst_analysis)
        assert x is not None
        produced_lemma, wc = x
        fst_analysis_to_fst_lemma_wc[fst_analysis] = produced_lemma, wc
        if produced_lemma not in l_to_analyses:
            produced_extra_lemmas.append(produced_lemma)

    produced_extra_lemma_to_analysis = cast(
        Dict[FSTLemma, Set[ConcatAnalysis]],
        expensive.strict_analyzer.bulk_lookup(produced_extra_lemmas),
    )

    for fst_analysis in chain.from_iterable(produced_extra_lemma_to_analysis.values()):
        x = fst_analysis_parser.extract_lemma_text_and_word_class(fst_analysis)
        assert x is not None
        produced_lemma, wc = x
        fst_analysis_to_fst_lemma_wc[fst_analysis] = produced_lemma, wc

    all_lemma_to_analysis = l_to_analyses.copy()
    all_lemma_to_analysis.update(produced_extra_lemma_to_analysis)

    no_analysis_counter = 0

    no_match_counter = 0

    success_counter = 0
    dup_counter = 0

    inconsistency_collection = InconsistencyCollection()

    for xml_l, analyses in l_to_analyses.items():

        if len(analyses) == 0:

            for entry in crkeng_xml.filter(l=xml_l):
                inconsistency_collection.add(ImportInconsistency(entry, "no analysis"))
                as_is_entries.append(entry)
                logger.debug(
                    "xml entry %s with pos %s ic %s can not be analyzed by fst strict analyzer"
                    % (xml_l, entry.pos, entry.ic)
                )
                no_analysis_counter += 1

        else:

            possible_lemma_analyses: List[ConcatAnalysis] = []
            for analysis in analyses:
                fst_lemma, wc = fst_analysis_to_fst_lemma_wc[analysis]
                fst_lemma_analyses = all_lemma_to_analysis[fst_lemma]

                for fst_lemma_analysis in fst_lemma_analyses:
                    x = fst_analysis_parser.extract_lemma_text_and_word_class(
                        fst_lemma_analysis
                    )
                    assert x is not None
                    wordform, wc = x
                    if wc is wc and wordform == fst_lemma:
                        possible_lemma_analyses.append(fst_lemma_analysis)

            for entry in crkeng_xml.filter(
                l=xml_l
            ):  # use pos, ic to determine which one the analysis is

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
                    fst_lemma, wc = fst_analysis_to_fst_lemma_wc[analysis]

                    is_match = does_inflectional_category_match_xml_entry(
                        wc, entry.pos, entry.ic
                    )
                    if is_match:
                        ambiguities.add(analysis)
                        wordform_to_ambiguous_analyses[fst_lemma].add(analysis)

                # there's only one identically matching wordform, just use that one
                for (
                    wordform,
                    ambiguous_analyses,
                ) in wordform_to_ambiguous_analyses.items():
                    if wordform == xml_l and len(ambiguous_analyses) == 1:
                        ambiguities = ambiguous_analyses
                        break

                if len(ambiguities) == 0:
                    inconsistency_collection.add(
                        ImportInconsistency(
                            entry, "pos conflict", possible_lemma_analyses
                        )
                    )
                    logger.debug(
                        "xml entry %s with pos %s ic %s have analyses by fst strict analyzer. "
                        "Yet all analyses conflict with the pos/ic in xml file"
                        % (xml_l, entry.pos, entry.ic)
                    )
                    as_is_entries.append(entry)
                    no_match_counter += 1

                elif len(ambiguities) == 1:  # nice
                    fst_analysis = ambiguities.pop()
                    entry_to_analysis[entry] = ConcatAnalysis(fst_analysis)
                    success_counter += 1
                else:
                    # check if it contains default forms of lemma analyses
                    res = crk_default_lemma_picker.get_lemma(ambiguities)
                    if res is not None:
                        entry_to_analysis[entry] = res
                        success_counter += 1
                    else:
                        inconsistency_collection.add(
                            ImportInconsistency(
                                entry, "multiple analyses", possible_lemma_analyses
                            )
                        )
                        logger.debug(
                            "xml entry %s with pos %s ic %s have more "
                            "than one potential analyses by fst strict analyzer."
                            % (xml_l, entry.pos, entry.ic)
                        )
                        as_is_entries.append(entry)
                        dup_counter += 1

    logger.info(
        f"{Fore.GREEN}%d entries found proper lemma analysis{Fore.RESET}"
        % success_counter
    )
    logger.info(
        f"{Fore.BLUE}There are %d entries that the fst can not give any analyses.{Fore.RESET}"
        % no_analysis_counter
    )
    logger.info(
        f"{Fore.BLUE}There are %d entries that do not have proper lemma analysis by fst{Fore.RESET}"
        % no_match_counter
    )

    logger.info(
        f"{Fore.BLUE}There are %d entries that have ambiguous lemma analyses{Fore.RESET}"
        % dup_counter
    )
    logger.info(
        f"{Fore.BLUE}These words will be labeled 'as-is', meaning their lemmas are undetermined.{Fore.RESET}"
    )

    if write_out_inconsistencies:
        output_file = inconsistency_collection.write_to_disk(
            Path("import-inconsistencies")
        )
        logger.info(f"Wrote inconsistency report to {output_file}")

    return entry_to_analysis, as_is_entries
