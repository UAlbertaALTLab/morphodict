import json
import xml.etree.ElementTree as ET
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from xml.dom import minidom

from django.core.management import BaseCommand
from tqdm import tqdm


class Command(BaseCommand):
    help = """Convert basic JSON format dictionary to XML

    Expects JSON format:
    [
        {
            "text": "gūts'ítō / gūts'átō",
            "word_class": "Noun",
            "defns": [
                "someone's body"
            ]
        },
        ⋮
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.add_argument("json_file")

    def handle(self, *args, json_file, **options):
        with open(json_file, "r") as f:
            dictionary_data = json.load(f)

        root = ET.Element("r")

        source = ET.Element("source")
        source.set("id", "OS")
        title = ET.Element("title")
        title.text = "Onespot-Sapir"
        source.append(title)
        root.append(source)

        for v in tqdm(dictionary_data):

            e = ET.SubElement(root, "e")
            lg = ET.SubElement(e, "lg")
            l = ET.SubElement(lg, "l")
            l.set("pos", v["word_class"])
            l.text = v["text"]
            lc = ET.SubElement(lg, "lc")
            lc.text = v["word_class"]

            mg = ET.SubElement(e, "mg")
            for defn in v["defns"]:
                tg = ET.SubElement(mg, "tg")
                t = ET.SubElement(tg, "t")
                t.text = defn
                t.set("sources", "TG")

        xml_string = ET.tostring(root)
        # pretty
        xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")

        with open("srseng.xml", "w") as f:
            f.write(xml_string)
