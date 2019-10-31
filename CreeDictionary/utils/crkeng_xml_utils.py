import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Set, Optional

from constants import LC


def convert_lc_str(lc: str) -> Optional[LC]:
    """
    convert <lc> in xml to one of the recognizable LexicalCategory Enum. Or None if not recognizable
    """

    if lc.startswith("VTA"):
        return LC.VTA
    if lc.startswith("VTI"):
        return LC.VTI
    if lc.startswith("VAI"):
        return LC.VAI
    if lc.startswith("VII"):
        return LC.VII
    if lc.startswith("NDA"):
        return LC.NAD
    if lc.startswith("NI"):
        return LC.NI
    if lc.startswith("NDI"):
        return LC.NID
    if lc.startswith("NA"):
        return LC.NA

    if lc.startswith("IPC"):
        return LC.IPC

    return None


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
