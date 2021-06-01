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
        [
            "achehtin",
            "it catches, does not fit"
        ],
        [
            "achimaw",
            "v.t., he is spoken of"
        ],
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
        source.set("id", "LLR")
        title = ET.Element("title")
        title.text = "Lac La Ronge"
        source.append(title)
        root.append(source)

        for wordform, definition in tqdm(dictionary_data):
            e = ET.SubElement(root, "e")
            lg = ET.SubElement(e, "lg")
            l = ET.SubElement(lg, "l")
            l.set("pos", "IPC")
            l.text = wordform
            lc = ET.SubElement(lg, "lc")
            lc.text = "IPC"

            mg = ET.SubElement(e, "mg")
            tg = ET.SubElement(mg, "tg")
            t = ET.SubElement(tg, "t")
            t.text = definition
            t.set("sources", "LLR")

        xml_string = ET.tostring(root)
        # pretty
        xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")

        with open("cwdeng.xml", "w") as f:
            f.write(xml_string)
