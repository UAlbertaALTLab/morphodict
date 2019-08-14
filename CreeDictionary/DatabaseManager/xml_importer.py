import sys
from os import path

import xml.etree.ElementTree as ET

from colorama import Fore
from tqdm import tqdm

from DatabaseManager import xml_entry_lemma_finder
from constants import PathLike
from typing import Union, Dict, List, Set, Tuple

import django
import os

from DatabaseManager.cree_inflection_generator import expand_inflections

sys.path.append(path.join(path.dirname(__file__), ".."))
os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()

from API.models import Definition, Inflection


def clear_database():
    Definition.objects.all().delete()
    Inflection.objects.all().delete()
    print("All Objects deleted from Database")


def generate_as_is_analysis(pos: str, lc: str):
    """
    generate analysis for xml entries whose fst analysis cannot be determined.
    The philosophy is to show lc if possible (which is more detailed), with pos being the fall back
    """

    # possible parsed pos str
    # {'', 'IPV', 'Pron', 'N', 'Ipc', 'V', '-'}

    # possible parsed lc str
    # {'', 'NDA-1', 'NDI-?', 'NA-3', 'NA-4w', 'NDA-2', 'VTI-2', 'NDI-3', 'NDI-x', 'NDA-x',
    # 'IPJ  Exclamation', 'NI-5', 'NDA-4', 'VII-n', 'NDI-4', 'VTA-2', 'IPH', 'IPC ;; IPJ',
    # 'VAI-v', 'VTA-1', 'NI-3', 'VAI-n', 'NDA-4w', 'IPJ', 'PrI', 'NA-2', 'IPN', 'PR', 'IPV',
    # 'NA-?', 'NI-1', 'VTA-3', 'NI-?', 'VTA-4', 'VTI-3', 'NI-2', 'NA-4', 'NDI-1', 'NA-1', 'IPP',
    # 'NI-4w', 'INM', 'VTA-5', 'PrA', 'NDI-2', 'IPC', 'VTI-1', 'NI-4', 'NDA-3', 'VII-v', 'Interr'}

    if lc != "":
        if "-" in lc:
            return lc.split("-")[0]
        else:
            return lc
    else:
        return pos


def import_crkeng_xml(filename: PathLike):
    """
    CLEARS the database and import from an xml file
    """

    clear_database()
    print("Database cleared")

    root = ET.parse(filename).getroot()

    source_ids = [s.get("id") for s in root.findall(".//source")]

    print("Sources parsed:", *source_ids)

    # value is definition object and its source as string
    xml_lemma_pos_lc_to_str_definitions = (
        {}
    )  # type: Dict[Tuple[str,str,str], List[Tuple[str, List[str]]]]

    # One lemma could have multiple entries with different pos and lc
    xml_lemma_to_pos_lc = {}  # type: Dict[str, List[Tuple[str,str]]]

    # def_to_inflections = dict()  # type: Dict[str, List[str]]
    # xml_lemma_to_inflections = dict()  # type: Dict[str, List[str]]

    elements = root.findall(".//e")
    print("%d dictionary entries found" % len(elements))

    duplicate_xml_lemma_pos_lc_count = 0
    print("extracting (xml_lemma, pos, lc) tuples")
    tuple_count = 0
    for element in elements:

        str_definitions_for_entry = []  # type: List[Tuple[str, List[str]]]
        for t in element.findall(".//mg//tg//t"):
            # definition.save()
            # for source_id in t.get("sources").split(" "):
            #     definition.sources.add(source_id_to_obj[source_id])
            str_definitions_for_entry.append((t.text, t.get("sources").split(" ")))

        l = element.find("lg/l")
        lc_str = element.find("lg/lc").text
        if lc_str is None:
            lc_str = ""
        xml_lemma, pos_str = l.text, l.get("pos")

        duplicate_lemma_pos_lc = False

        if xml_lemma in xml_lemma_to_pos_lc:

            if (pos_str, lc_str) in xml_lemma_to_pos_lc[xml_lemma]:
                duplicate_xml_lemma_pos_lc_count += 1
                duplicate_lemma_pos_lc = True
            else:
                tuple_count += 1
                xml_lemma_to_pos_lc[xml_lemma].append((pos_str, lc_str))
        else:
            tuple_count += 1
            xml_lemma_to_pos_lc[xml_lemma] = [(pos_str, lc_str)]

        # todo: tests if definition are really merged
        if duplicate_lemma_pos_lc:
            xml_lemma_pos_lc_to_str_definitions[(xml_lemma, pos_str, lc_str)].extend(
                str_definitions_for_entry
            )
        else:
            xml_lemma_pos_lc_to_str_definitions[
                (xml_lemma, pos_str, lc_str)
            ] = str_definitions_for_entry

    print(Fore.BLUE)
    print(
        "%d entries have (lemma, pos, lc) duplicate to others. Their definition will be merged"
        % duplicate_xml_lemma_pos_lc_count
    )
    print(Fore.RESET)
    print("%d (xml_lemma, pos, lc) tuples extracted" % tuple_count)
    xml_lemma_pos_lc_to_analysis = xml_entry_lemma_finder.extract_fst_lemmas(
        xml_lemma_to_pos_lc
    )

    # these two will be imported to the database
    as_is_xml_lemma_pos_lc = []  # type: List[Tuple[str, str, str]]
    true_lemma_analyses_to_xml_lemma_pos_lc = (
        dict()
    )  # type: Dict[str, List[Tuple[str, str, str]]]

    dup_analysis_xml_lemma_pos_lc_count = 0

    for (xml_lemma, pos, lc), analysis in xml_lemma_pos_lc_to_analysis.items():
        if analysis != "":
            if analysis in true_lemma_analyses_to_xml_lemma_pos_lc:
                dup_analysis_xml_lemma_pos_lc_count += 1

                # merge definition to the first (lemma, pos, lc)
                xml_lemma_pos_lc_to_str_definitions[
                    true_lemma_analyses_to_xml_lemma_pos_lc[analysis][0]
                ].extend(xml_lemma_pos_lc_to_str_definitions[(xml_lemma, pos, lc)])

                true_lemma_analyses_to_xml_lemma_pos_lc[analysis].append(
                    (xml_lemma, pos, lc)
                )
            else:
                true_lemma_analyses_to_xml_lemma_pos_lc[analysis] = [
                    (xml_lemma, pos, lc)
                ]
        else:
            as_is_xml_lemma_pos_lc.append((xml_lemma, pos, lc))

    print(Fore.BLUE)
    print(
        "%d (lemma, pos, lc) have duplicate fst lemma analysis to others.\nTheir definition will be merged"
        % dup_analysis_xml_lemma_pos_lc_count
    )
    print(Fore.RESET)

    inflection_counter = 1
    definition_counter = 1

    db_inflections = []  # type: List[Inflection]
    db_definitions = []  # type: List[Definition]
    for xml_lemma, pos, lc in tqdm(
        as_is_xml_lemma_pos_lc, desc="importing 'as-is' words"
    ):

        db_inflection = Inflection(
            id=inflection_counter,
            text=xml_lemma,
            analysis=generate_as_is_analysis(pos, lc),
            is_lemma=True,
            as_is=True,
        )
        inflection_counter += 1
        db_inflections.append(db_inflection)

        str_definitions_source_strings = xml_lemma_pos_lc_to_str_definitions[
            (xml_lemma, pos, lc)
        ]
        for str_definition, source_strings in str_definitions_source_strings:
            db_definition = Definition(
                id=definition_counter,
                text=str_definition,
                sources=" ".join(source_strings),
                lemma=db_inflection,
            )
            definition_counter += 1
            db_definitions.append(db_definition)
    # print(len(db_inflections))

    expanded = expand_inflections(
        list(true_lemma_analyses_to_xml_lemma_pos_lc.keys())[:10]
    )

    for true_lemma_analysis, xml_lemma_pos_lcs in tqdm(
        list(true_lemma_analyses_to_xml_lemma_pos_lc.items())[:10],
        desc="importing generated inflections",
    ):
        for generated_analysis, generated_inflections in expanded[true_lemma_analysis]:
            db_lemmas = []
            if generated_analysis != true_lemma_analysis:
                is_lemma = False
            else:
                is_lemma = True

            for generated_inflection in generated_inflections:
                db_inflection = Inflection(
                    text=generated_inflection,
                    analysis=generated_analysis,
                    is_lemma=is_lemma,
                    as_is=False,
                )

                db_inflection.save()
                if is_lemma:
                    db_lemmas.append(db_inflection)

            if is_lemma:

                str_definitions_source_strings = xml_lemma_pos_lc_to_str_definitions[
                    xml_lemma_pos_lcs[0]
                ]

                for str_definition, source_strs in str_definitions_source_strings:
                    db_definition = Definition(context=str_definition)
                    db_definition.save()
                    for source_id in source_strs:
                        db_definition.sources.add(source_id_to_obj[source_id])
                    for db_lemma in db_lemmas:
                        db_lemma.definitions.add(db_definition)

    Inflection.objects.bulk_create(db_inflections)
    Definition.objects.bulk_create(db_definitions)
