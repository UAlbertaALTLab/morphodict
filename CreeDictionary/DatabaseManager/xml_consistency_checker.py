"""check the consistency of a xml source with a fst"""
from typing import Optional

from constants import InflectionCategory


def parse_xml_lc(lc_text: str) -> Optional[InflectionCategory]:
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
) -> bool:
    """
    check whether a xml entry is "compatible" with an `InflectionCategory`

    Note: xml entries are underspecified: meaning they can say 'V' in pos but nothing in lc

    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, 'V', '')
    True
    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, 'V', 'VTI-?')
    True

    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, '', '')
    False
    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, 'V', 'VAI-2')
    False
    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, 'N', '')
    False
    >>> does_hfstol_xml_pos_match(InflectionCategory.VTI, 'V', 'Nonsense Garbage Garbage')
    False
    """

    if (
        (xml_pos == "V" and hfstol_category.is_verb())
        or (xml_pos == "N" and hfstol_category.is_noun())
        or (xml_pos == "Ipc" and hfstol_category is InflectionCategory.IPC)
        or (xml_pos == "Pron" and hfstol_category is InflectionCategory.Pron)
    ):
        lc_category = parse_xml_lc(xml_lc)

        if xml_lc == "" or hfstol_category is lc_category:
            return True
        else:
            return False
    else:
        return False
