"""check the consistency of a xml source with a fst"""

from CreeDictionary.utils import WordClass
from CreeDictionary.utils.crkeng_xml_utils import (
    convert_xml_inflectional_category_to_word_class,
)


def does_inflectional_category_match_xml_entry(
    inflectional_category: WordClass, xml_pos: str, xml_ic: str
) -> bool:
    """
    check whether an xml entry matches with an `InflectionCategory`
        if neither xml_pos and xml_ic are understood: False

        if only xml_pos is understood: check if xml_pos matches ic

        if both xml_pos and xml_ic are understood: check both

    xml entries are underspecified: both xml_pos xml_ic can be empty string

    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, 'V', '')
    True
    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, 'V', 'VTI-?')
    True
    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, '', '')
    False
    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, 'V', 'VAI-2')
    False
    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, 'N', '')
    False
    >>> does_inflectional_category_match_xml_entry(WordClass.VTI, 'V', 'IJFIJFIJSAJDIAIDJRN')
    True
    """

    if (
        (xml_pos == "V" and inflectional_category.is_verb())
        or (xml_pos == "N" and inflectional_category.is_noun())
        or (xml_pos == "Ipc" and inflectional_category is WordClass.IPC)
        or (xml_pos == "Pron" and inflectional_category is WordClass.Pron)
    ):
        wc = convert_xml_inflectional_category_to_word_class(xml_ic)

        if (
            wc is None or xml_ic == ""
        ):  # e.g. niya has xml_pos Pron, xml_ic PrA, PrA will gives None
            return True

        if inflectional_category is wc:
            return True
        else:
            return False
    else:
        return False
