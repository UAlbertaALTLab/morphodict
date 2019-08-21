from pathlib import Path
from typing import Set
import xml.etree.ElementTree as ET


def get_xml_lemma_set(filename: Path) -> Set[str]:
    elements = ET.parse(str(filename)).getroot().findall(".//e")
    return {extract_l_str(element) for element in elements}


def extract_l_str(element: ET.Element) -> str:
    """
    receives <e> element and get <l> string. raises ValueError if <l> not found or <l> has empty text
    """
    l_element = element.find("lg/l")
    if l_element is None:
        raise ValueError(
            f"<l> not found while trying to extract text from entry \n {ET.tostring(element, encoding='unicode')}"
        )
    text = l_element.text
    if text == "" or text is None:
        raise ValueError(
            f"<l> has empty text in entry \n {ET.tostring(element, encoding='unicode')}"
        )
    return text
