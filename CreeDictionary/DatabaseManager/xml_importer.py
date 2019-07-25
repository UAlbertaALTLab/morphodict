import sys
from os import path

import xml.etree.ElementTree as ET
from os.path import dirname
from pathlib import Path
from typing import Union, Dict, List, Set

import django
import os

sys.path.append(path.join(path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CreeDictionary.settings'
django.setup()

from API.models import Definition, Source, Inflection

PathLike = Union[str, Path]  # python 3.5 compatible

def clear_database():
    Definition.objects.all().delete()
    Source.objects.all().delete()
    Inflection.objects.all().delete()
    print('All Objects deleted from Database')


def import_crkeng_xml(filename: PathLike):
    """
    CLEARS the database and import from an xml file
    """

    clear_database()
    print('Database cleared')

    root = ET.parse(filename).getroot()

    source_ids = [s.get('id') for s in root.findall('.//source')]

    print('Sources parsed:', *source_ids)

    source_id_to_obj = {source_id: Source(name=source_id) for source_id in source_ids}  # type: Dict[str, Source]

    for s in source_id_to_obj.values():
        s.save()

    # gather all lemmas from xml to generate their inflection in bulk
    xml_lemma_to_db_definitions = {}  # type: Dict[str, List[Definition]]
    xml_lemma_to_pos = {}  # type: Dict[str, str]

    # def_to_inflections = dict()  # type: Dict[str, List[str]]
    # xml_lemma_to_inflections = dict()  # type: Dict[str, List[str]]

    elements = root.findall(".//e")
    for element in elements:

        group = []  # type: List[Definition]
        for t in element.findall('.//mg//tg//t'):
            definition = Definition(context=t.text)
            for source_id in t.get('sources').split(' '):
                definition.sources.add(source_id_to_obj[source_id])
            group.append(definition)

        l = element.find('lg/l')
        xml_lemma, pos = l.text, l.get('pos')
        xml_lemma_to_db_definitions[xml_lemma] = group
        xml_lemma_to_pos[xml_lemma] = pos








    # todo: save defs

    # b = root.findall(".//e//mg//tg/t")
    # print(a[0].text)
    # print(a[0].get('pos'))
    # print(xmlLemmas[:3])
