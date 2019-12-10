"""check the consistency of a xml source with a fst"""

from constants import SimpleLexicalCategory
from utils.crkeng_xml_utils import parse_xml_lc


def does_lc_match_xml_entry(
    lc: SimpleLexicalCategory, xml_pos: str, xml_lc: str
) -> bool:
    """
    check whether an xml entry matches with an `InflectionCategory`
        if neither xml_pos and xml_lc are understood: False
        
        if only xml_pos is understood: check if xml_pos matches lc

        if both xml_pos and xml_lc are understood: check both

    xml entries are underspecified: both xml_pos xml_lc can be empty string

    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, 'V', '')
    True
    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, 'V', 'VTI-?')
    True
    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, '', '')
    False
    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, 'V', 'VAI-2')
    False
    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, 'N', '')
    False
    >>> does_lc_match_xml_entry(SimpleLexicalCategory.VTI, 'V', 'IJFIJFIJSAJDIAIDJRN')
    True
    """

    if (
        (xml_pos == "V" and lc.is_verb())
        or (xml_pos == "N" and lc.is_noun())
        or (xml_pos == "Ipc" and lc is SimpleLexicalCategory.IPC)
        or (xml_pos == "Pron" and lc is SimpleLexicalCategory.Pron)
    ):
        simple_lc = parse_xml_lc(xml_lc)

        if (
            simple_lc is None or xml_lc == ""
        ):  # e.g. niya has xml_pos Pron, xml_lc PrA, PrA will gives None
            return True

        if lc is simple_lc:
            return True
        else:
            return False
    else:
        return False
