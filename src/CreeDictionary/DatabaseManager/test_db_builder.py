"""
build test_db.sqlite3 from res/test_db_words.txt
"""

import logging
import xml.etree.ElementTree as ET
from typing import Set

from tqdm import tqdm

from CreeDictionary.DatabaseManager.xml_importer import find_latest_xml_file
from CreeDictionary.shared import expensive
from CreeDictionary.utils import crkeng_xml_utils, fst_analysis_parser, shared_res_dir
from CreeDictionary.utils.crkeng_xml_utils import extract_l_str
from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from CreeDictionary.utils.profiling import timed

logger = logging.getLogger(__name__)


def get_test_words() -> Set[str]:
    """
    get manually specified test words from res/test_db_words.txt

    >>> assert "wâpamêw" in get_test_words()
    """
    lines = (shared_res_dir / "test_db_words.txt").read_text().splitlines()
    words = set()
    for line in lines:
        line = line.strip()
        if line and line[0] != "#":
            words.add(line)

    return words


@timed()
def build_test_xml():
    """
    Determine relevant entries in crkeng.xml and build a smaller xml file for testing.
    """

    crkeng_file_path = find_latest_xml_file(shared_res_dir / "dictionaries")

    print(f"Building test dictionary files using {crkeng_file_path.name}")

    crkeng_root = ET.parse(str(crkeng_file_path)).getroot()

    # relevant entries in crkeng.xml file we want to determine
    relevant_xml_ls: Set[str] = set()

    xml_ls: Set[str] = set()
    crkeng_entries = crkeng_root.findall(".//e")
    for element in crkeng_entries:
        xml_l = extract_l_str(element)
        xml_ls.add(xml_l)

    test_words = get_test_words()

    print(f"Analyzing xml l elements and test words")
    word_to_analyses = expensive.relaxed_analyzer().bulk_lookup(xml_ls | test_words)
    print("Analysis done")

    test_word_lemmas: Set[str] = set()

    for test_word in test_words:
        for analysis in word_to_analyses[test_word]:
            lemma = fst_analysis_parser.extract_lemma(analysis)
            if lemma is None:
                logger.warn(
                    "Skipping test word: %s. "
                    "Could not extract lemma from its analysis: %s",
                    test_word,
                    analysis,
                )
                continue
            test_word_lemmas.add(lemma)

    for xml_l in tqdm(xml_ls, desc="screening relevant entries in crkeng.xml"):
        if xml_l in test_words:
            relevant_xml_ls.add(xml_l)
            continue
        for xml_l_analysis in word_to_analyses[xml_l]:
            xml_lemma = partition_analysis(xml_l_analysis)[1]
            for test_word_lemma in test_word_lemmas:
                if test_word_lemma == xml_lemma:
                    relevant_xml_ls.add(xml_l)
                    break

    relevant_crkeng_entries = []

    for element in crkeng_entries:
        xml_l = extract_l_str(element)
        if xml_l in relevant_xml_ls:
            relevant_crkeng_entries.append(element)

    crkeng_xml_utils.write_xml_from_elements(
        list(crkeng_root.findall(".//source")) + relevant_crkeng_entries,
        shared_res_dir / "test_dictionaries" / "crkeng.xml",
    )
