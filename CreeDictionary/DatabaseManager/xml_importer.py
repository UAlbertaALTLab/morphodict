import sys
from os import path

import xml.etree.ElementTree as ET
from constants import PathLike
from typing import Union, Dict, List, Set, Tuple

import django
import os

from DatabaseManager.cree_inflection_generator import expand

sys.path.append(path.join(path.dirname(__file__), ".."))
os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()

from API.models import Definition, Source, Inflection


def clear_database():
    Definition.objects.all().delete()
    Source.objects.all().delete()
    Inflection.objects.all().delete()
    print("All Objects deleted from Database")


def import_crkeng_xml(filename: PathLike):
    """
    CLEARS the database and import from an xml file
    """

    clear_database()
    print("Database cleared")

    root = ET.parse(filename).getroot()

    source_ids = [s.get("id") for s in root.findall(".//source")]

    print("Sources parsed:", *source_ids)

    source_id_to_obj = {
        source_id: Source(name=source_id) for source_id in source_ids
    }  # type: Dict[str, Source]

    for s in source_id_to_obj.values():
        s.save()

    # pos_set = set()
    # lc_set = set()
    # gather all lemmas from xml to generate their inflection in bulk
    xml_lemma_to_db_definitions = {}  # type: Dict[str, List[Definition]]

    # One lemma could have multiple entries with different pos and lc
    xml_lemma_to_pos_lc = {}  # type: Dict[str, List[Tuple[str,str]]]

    # def_to_inflections = dict()  # type: Dict[str, List[str]]
    # xml_lemma_to_inflections = dict()  # type: Dict[str, List[str]]

    elements = root.findall(".//e")

    print("%d dictionary entries found" % len(elements))
    for element in elements:

        group = []  # type: List[Definition]
        for t in element.findall(".//mg//tg//t"):
            definition = Definition(context=t.text)
            # for source_id in t.get('sources').split(' '):
            #     definition.sources.add(source_id_to_obj[source_id])
            group.append(definition)

        l = element.find("lg/l")
        lc_str = element.find("lg/lc").text
        xml_lemma, pos_str = l.text, l.get("pos")
        xml_lemma_to_db_definitions[xml_lemma] = group
        if xml_lemma in xml_lemma_to_pos_lc:
            xml_lemma_to_pos_lc[xml_lemma].append((pos_str, lc_str))
        else:
            xml_lemma_to_pos_lc[xml_lemma] = [(pos_str, lc_str)]

    expanded = expand(xml_lemma_to_pos_lc)

    # pos_set.add(pos_str)
    # lc_set.add(lc_str)

    pass
    # print(pos_set)
    # print(lc_set)
    # todo: save defs

    # b = root.findall(".//e//mg//tg/t")
    # print(a[0].text)
    # print(a[0].get('pos'))
    # print(xmlLemmas[:3])
