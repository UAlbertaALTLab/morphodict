import logging
import xml.etree.ElementTree as ET
from collections import defaultdict
from itertools import chain
from pathlib import Path
from typing import (
    DefaultDict,
    Dict,
    Hashable,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    TextIO,
    Tuple,
    Union,
    cast,
)
from xml.dom import minidom
from xml.etree import ElementTree as ET

from utils import WordClass
from utils.data_classes import XMLEntry, XMLTranslation
from utils.types import HashableNamedTupleFieldValue, NamedTupleFieldName

logger = logging.getLogger(__name__)


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


def convert_xml_inflectional_category_to_word_class(
    ic_text: str,
) -> Optional[WordClass]:
    """
    return recognized ic, None if not recognized

    :param ic_text: 2019 July, all `lc` from crkeng.xml are
        {'NDA-1', None, 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
        'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
        'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
        'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
        'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}
    :return:
    """
    if ic_text is None:
        return None
    if ic_text.startswith("VTA"):
        return WordClass.VTA
    if ic_text.startswith("VTI"):
        return WordClass.VTI
    if ic_text.startswith("VAI"):
        return WordClass.VAI
    if ic_text.startswith("VII"):
        return WordClass.VII
    if ic_text.startswith("NDA"):
        return WordClass.NAD
    if ic_text.startswith("NI"):
        return WordClass.NI
    if ic_text.startswith("NDI"):
        return WordClass.NID
    if ic_text.startswith("NA"):
        return WordClass.NA

    if ic_text.startswith("IPC"):
        return WordClass.IPC
    if ic_text.startswith("IPV"):
        return WordClass.IPV

    return None


class IndexedXML(Iterable[XMLEntry]):
    """
    The collection of all entries parsed from the XML source file.
    It supports fast querying with field/field combinations by hashing the entries in advance.
    """

    # --- alias for type hints---
    Indexes = Dict[
        Tuple[NamedTupleFieldName, ...],
        Dict[Tuple[HashableNamedTupleFieldValue, ...], Set[XMLEntry]],
    ]

    # --- Instance attribute type hints ---
    _entries: Set[XMLEntry]
    _indexes: Indexes
    _source_abbreviations: Iterable[str]

    # --- Class attributes ---
    # Add key or key combinations here when it's needed to lookup with certain keys
    # order does not matter here, they will be sorted in the built index
    INDEX_KEYS: List[Tuple[NamedTupleFieldName, ...]] = [
        # (
        #     NamedTupleFieldName("l"),
        #     NamedTupleFieldName("pos"),
        #     NamedTupleFieldName("ic"),
        # ),
        (NamedTupleFieldName("l"),),
    ]

    def __iter__(self) -> Iterator[XMLEntry]:
        yield from self._entries

    @property
    def source_abbreviations(self) -> Iterable[str]:
        """
        acronyms of the sources, like "CW" for Cree Words
        """
        return self._source_abbreviations

    @staticmethod
    def _parse_translation_element(t_element: ET.Element) -> XMLTranslation:
        """
        Turn <t></t> inside <e></e> into a NamedTuple, which hosts a single translation of the entry

        :raises ValueError: with error message, when the <t> element has no text or when it
            doesn't have source="" attribute
        """

        raw_sources = t_element.get("sources")
        t_element_text = t_element.text
        if raw_sources is None:
            raise ValueError(
                f"<t> does not have a source attribute in the following entry \n {ET.tostring(t_element, encoding='unicode')}"
            )
        if t_element_text is None:
            raise ValueError(
                f"<t> has empty text in the following entry \n {ET.tostring(t_element, encoding='unicode')}"
            )

        sources = tuple(raw_sources.split(" "))
        text = t_element_text

        return XMLTranslation(text=text, sources=sources)

    @staticmethod
    def _parse_entry_element(element: ET.Element) -> XMLEntry:
        """
        Turn <e></e> inside crkeng.xml into NamedTuples
        """

        # reminder/type hints: values we are extracting to compose XMLEntry
        l: str
        pos: str
        ic: str
        stem: Optional[str]
        translations: Tuple[XMLTranslation, ...]

        # extract l
        l_element = element.find("lg/l")
        assert (
            l_element is not None
        ), f"Missing <l> element in the following entry: \n {ET.tostring(element, encoding='unicode')}"

        l_element_text = l_element.text
        if l_element_text == "" or l_element_text is None:
            raise ValueError(
                f"<l> has empty text in entry \n {ET.tostring(element, encoding='unicode')}"
            )
        l = l_element_text

        # extract pos
        maybe_pos = l_element.get("pos")
        assert (
            maybe_pos is not None
        ), f"<l> lacks pos attribute in entry \n {ET.tostring(element, encoding='unicode')}"
        pos = maybe_pos

        # extract ic
        ic_element = element.find("lg/lc")
        assert (
            ic_element is not None
        ), f"Missing <lc> element in entry \n {ET.tostring(element, encoding='unicode')}"

        ic_element_text = ic_element.text

        if ic_element_text is None:
            ic = ""
        else:
            ic = ic_element_text

        # extract stem
        stem_element = element.find("lg/stem")
        if stem_element is None:
            stem = None
        else:
            stem = stem_element.text

        # will cast to tuple later
        _translations: List[XMLTranslation] = []
        for t_element in element.findall(".//mg//tg//t"):
            try:
                _translations.append(IndexedXML._parse_translation_element(t_element))
            except ValueError as e:
                logger.error("Malformed <t></t> element")
                logger.error(e)
                continue

        translations = tuple(_translations)

        return XMLEntry(l=l, pos=pos, ic=ic, stem=stem, translations=translations)

    @classmethod
    def from_xml_file(cls, crkeng_xml: TextIO) -> "IndexedXML":
        """
        import entries from a given crkeng_xml
        """

        root = ET.parse(crkeng_xml).getroot()

        # we build entries by iterating over <e></e> in the xml file
        entries: Set[XMLEntry] = {
            cls._parse_entry_element(element) for element in root.findall(".//e")
        }

        source_abbreviations = []

        for s in root.findall(".//source"):
            abbreviation = s.get("id")
            assert abbreviation is not None
            source_abbreviations.append(abbreviation)

        return cls(entries=entries, source_abbreviations=source_abbreviations)

    @classmethod
    def _build_indexes(cls, entries: Set[XMLEntry]) -> Indexes:
        """
        build in-memory indexes for fast querying later
        """
        # first classify the entries by each field names
        # then we merge them by the key combinations needed

        # helper type hint
        _SingleKeyIndexes = Dict[
            NamedTupleFieldName, Dict[HashableNamedTupleFieldValue, Set[XMLEntry]]
        ]

        single_key_indexes: _SingleKeyIndexes = {}
        for field_name in set(chain(*cls.INDEX_KEYS)):
            field_value_to_entry = defaultdict(set)
            for entry in entries:
                field_value_to_entry[getattr(entry, field_name)].add(entry)
            single_key_indexes[field_name] = field_value_to_entry

        indexes: Dict[
            Tuple[NamedTupleFieldName, ...],
            Dict[Tuple[HashableNamedTupleFieldValue, ...], Set[XMLEntry]],
        ] = {tuple(sorted(field_names)): {} for field_names in cls.INDEX_KEYS}

        for sorted_field_names, values_to_entries in indexes.items():

            for entry in entries:
                values_to_entries[
                    tuple(
                        getattr(entry, field_name) for field_name in sorted_field_names
                    )
                ] = set.union(
                    *(
                        single_key_indexes[field_name][getattr(entry, field_name)]
                        for field_name in sorted_field_names
                    )
                )

        return indexes

    def __init__(self, entries: Set[XMLEntry], source_abbreviations: Iterable[str]):
        self._entries = entries
        self._source_abbreviations = source_abbreviations

        self._indexes = self._build_indexes(entries)

    def filter(self, **constraints: HashableNamedTupleFieldValue) -> Set[XMLEntry]:
        """
        A lookup method that mimics django's queryset API. Except the relevant indexes must be built in advance.
        The returned set is empty when no matching entries are found

        :raise ValueError: when the relevant index does not exist for the query
        """
        # sort by field names
        sorted_constraints = sorted(constraints.items(), key=lambda x: x[0])
        field_names, field_values = zip(*sorted_constraints)

        try:
            values_to_entries = self._indexes[
                cast(
                    Tuple[NamedTupleFieldName],
                    field_names,
                )
            ]
        except ValueError:
            raise ValueError(f"index with field names {list(constraints)} is not built")

        return values_to_entries.get(field_values, set())

    def values_list(
        self, *field_names, flat=False, named=False
    ) -> List[Union[tuple, NamedTuple, HashableNamedTupleFieldValue]]:
        """
        mimics django's QuerySet.values_list method

        :return:
        """
        if len(field_names) != 1 or not flat or named:
            raise NotImplementedError("Matt's been lazy <3")

        return [getattr(e, field_names[0]) for e in self._entries]
