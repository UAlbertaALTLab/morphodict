import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from typing import Iterable
from xml.dom import minidom

from constants import SimpleLexicalCategory


def write_xml_from_elements(elements: Iterable[ET.Element], target_file: Path):
    """
    It also creates parent directories if they don't exist. It overwrites existing xml file of the same name.

    :param elements:
    :param target_file: creates directories if not already exist
    :return:
    """
    text = "<r>"
    for element in elements:
        text += ET.tostring(element, encoding="unicode")
    text += "</r>"
    pretty_text = minidom.parseString(text).toprettyxml()
    target_file.parent.mkdir(exist_ok=True, parents=True)
    target_file.write_text(pretty_text)


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


def parse_xml_lc(lc_text: str) -> Optional[SimpleLexicalCategory]:
    """
    return recognized lc, None if not recognized

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
        return SimpleLexicalCategory.VTA
    if lc_text.startswith("VTI"):
        return SimpleLexicalCategory.VTI
    if lc_text.startswith("VAI"):
        return SimpleLexicalCategory.VAI
    if lc_text.startswith("VII"):
        return SimpleLexicalCategory.VII
    if lc_text.startswith("NDA"):
        return SimpleLexicalCategory.NAD
    if lc_text.startswith("NI"):
        return SimpleLexicalCategory.NI
    if lc_text.startswith("NDI"):
        return SimpleLexicalCategory.NID
    if lc_text.startswith("NA"):
        return SimpleLexicalCategory.NA

    if lc_text.startswith("IPC"):
        return SimpleLexicalCategory.IPC
    if lc_text.startswith("IPV"):
        return SimpleLexicalCategory.IPV

    return None
