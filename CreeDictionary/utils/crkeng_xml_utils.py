from pathlib import Path
from typing import Set
import xml.etree.ElementTree as ET


def get_xml_lemma_set(filename: Path) -> Set[str]:
    elements = ET.parse(str(filename)).getroot().findall(".//e")
    return {element.find("lg/l").text for element in elements}
