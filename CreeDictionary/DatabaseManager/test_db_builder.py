"""
build test_db.sqlite3 from res/test_db_words.txt
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from itertools import chain
from typing import List, Set, Dict

from tqdm import tqdm

from DatabaseManager.xml_importer import find_latest_xml_files
from utils.profiling import timed
from shared import descriptive_analyzer
from utils import shared_res_dir, fst_analysis_parser, crkeng_xml_utils
from utils.crkeng_xml_utils import extract_l_str


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
def build_test_xml(multi_processing: int = 2):
    """
    Determine relevant entries in crkeng.xml and build a smaller xml file for testing.
    """

    crkeng_file_path, engcrk_file_path = find_latest_xml_files(
        shared_res_dir / "dictionaries"
    )

    print(
        f"Building test dictionary files using {crkeng_file_path.name} and {crkeng_file_path.name}"
    )

    crkeng_root = ET.parse(str(crkeng_file_path)).getroot()
    engcrk_root = ET.parse(str(engcrk_file_path)).getroot()

    # relevant entries in crkeng.xml file we want to determine
    relevant_xml_lemmas: Set[str] = set()
    # relevant entries in engcrk.xml file we want to determine
    relevant_eng_words: Set[str] = set()

    xml_lemmas: Set[str] = set()
    crkeng_entries = crkeng_root.findall(".//e")
    for element in crkeng_entries:
        xml_lemma = extract_l_str(element)
        xml_lemmas.add(xml_lemma)

    engcrk_elements = engcrk_root.findall(".//e")
    eng_word_to_cree_words: Dict[str, List[str]] = defaultdict(list)
    for element in engcrk_elements:
        eng_element = element.find("lg/l")
        assert (
            eng_element is not None
        ), f"{str(ET.tostring(element))} does not have an l element"
        eng_word = eng_element.text

        # 2019/12/04: there is this fuckery in engcrk.xml, where l does not have a text (and pos is a strand of hair)
        """
        <e>
           <lg xml:lang="eng">
              <l pos="("></l>
           </lg>
           <mg>
           <tg xml:lang="crk">
              <trunc sources="CW">[single] hair of otter</trunc>
              <t rank="1.0" pos="N">nikikopîway</t>
           </tg>
           </mg>
        </e>
        """
        if eng_word is None:
            continue
        cree_word_elements = element.findall(".//tg//t")
        for cree_word_element in cree_word_elements:
            cree_word = cree_word_element.text
            assert cree_word is not None
            eng_word_to_cree_words[eng_word].append(cree_word)

    test_words = get_test_words()

    print(f"Analyzing xml lemmas and test words with {multi_processing} processes")
    word_to_analyses = descriptive_analyzer.feed_in_bulk_fast(
        xml_lemmas | test_words | set(chain(*eng_word_to_cree_words.values())),
        multi_process=multi_processing,
    )
    print("Analysis done")

    test_word_lemmas: Set[str] = set()

    for test_word in test_words:
        for analysis in word_to_analyses[test_word]:
            lemma = fst_analysis_parser.extract_lemma(analysis)
            assert lemma is not None
            test_word_lemmas.add(lemma)

    for xml_lemma in tqdm(xml_lemmas, desc="screening relevant entries in crkeng.xml"):
        if xml_lemma in test_words:
            relevant_xml_lemmas.add(xml_lemma)
            continue
        for xml_lemma_analysis in word_to_analyses[xml_lemma]:
            for test_word_lemma in test_word_lemmas:
                if test_word_lemma in xml_lemma_analysis:
                    relevant_xml_lemmas.add(xml_lemma)
                    break

    for eng_word in tqdm(
        eng_word_to_cree_words, desc="screening relevant entries in engcrk.xml"
    ):
        assert isinstance(eng_word, str)  # mypy is being stupid
        for engcrk_cree_word in eng_word_to_cree_words[eng_word]:
            for analysis in word_to_analyses[engcrk_cree_word]:
                lemma = fst_analysis_parser.extract_lemma(analysis)
                if lemma in test_word_lemmas:
                    relevant_eng_words.add(eng_word)
                    break

    relevant_crkeng_entries = []

    for element in crkeng_entries:
        xml_lemma = extract_l_str(element)
        if xml_lemma in relevant_xml_lemmas:
            relevant_crkeng_entries.append(element)

    relevant_engcrk_entries = []

    for element in engcrk_elements:
        eng_element = element.find("lg/l")
        assert eng_element is not None
        eng_word = eng_element.text
        if eng_word in relevant_eng_words:
            relevant_engcrk_entries.append(element)

    crkeng_xml_utils.write_xml_from_elements(
        list(crkeng_root.findall(".//source")) + relevant_crkeng_entries,
        shared_res_dir / "test_dictionaries" / "crkeng.xml",
    )

    crkeng_xml_utils.write_xml_from_elements(
        relevant_engcrk_entries, shared_res_dir / "test_dictionaries" / "engcrk.xml"
    )
