"""
build test_db.sqlite3 from res/test_db_words.txt
"""

import xml.etree.ElementTree as ET
from typing import List, Set

from shared import strict_analyzer
from utils import shared_res_dir, fst_analysis_parser
from utils.crkeng_xml_utils import extract_l_str


def get_test_words() -> List[str]:
    """
    get manually specified test words from res/test_db_words.txt

    >>> assert "wâpamêw" in get_test_words()
    """
    lines = (shared_res_dir / "test_db_words.txt").read_text().splitlines()
    words = []
    for line in lines:
        line = line.strip()
        if line and line[0] != "#":
            words.append(line)

    return words


def build_test_xml(multi_processing: int = 2):
    """
    Determine relevant entries in crkeng.xml and build a smaller xml file for testing.
    """

    root = ET.parse(str(shared_res_dir / "dictionaries" / "crkeng.xml")).getroot()

    # relevant entries in crkeng.xml file we want to determine
    relevant_xml_lemmas: Set[str] = set()

    xml_lemmas = []
    elements = root.findall(".//e")
    for element in elements:
        xml_lemma = extract_l_str(element)
        xml_lemmas.append(xml_lemma)

    test_words = get_test_words()

    print(f"Analyzing xml lemmas and test words with {multi_processing} processes")
    word_to_analyses = strict_analyzer.feed_in_bulk_fast(
        xml_lemmas + test_words, multi_process=multi_processing
    )
    print("Analysis done")

    test_word_lemmas: Set[str] = set()

    for test_word in test_words:
        for analysis in word_to_analyses[test_word]:
            lemma = fst_analysis_parser.extract_lemma(analysis)
            assert lemma is not None
            test_word_lemmas.add(lemma)

    for xml_lemma in xml_lemmas:
        for xml_lemma_analysis in word_to_analyses[xml_lemma]:
            for test_word_lemma in test_word_lemmas:
                if test_word_lemma in xml_lemma_analysis:
                    relevant_xml_lemmas.add(xml_lemma)
                    break
