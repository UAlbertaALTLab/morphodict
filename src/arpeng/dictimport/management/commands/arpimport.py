import json
import xml.etree.ElementTree as ET
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from xml.dom import minidom

from django.core.management import BaseCommand
from tqdm import tqdm


class Command(BaseCommand):
    help = """Convert arapaho_lexicon.json dictionary to XML
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.add_argument("json_file")

    def handle(self, *args, json_file, **options):
        with open(json_file, "r") as f:
            dictionary_data = json.load(f)

        root = ET.Element("r")

        source = ET.Element("source")
        source.set("id", "ALD")
        title = ET.Element("title")
        title.text = "Arapaho Lexical Dictionary"
        source.append(title)
        root.append(source)

        for v in tqdm(dictionary_data.values()):
            if not v["senses"] or "definition" not in v["senses"][0]:
                continue
            if v.get("status", None) == "deleted":
                continue

            e = ET.SubElement(root, "e")
            lg = ET.SubElement(e, "lg")
            l = ET.SubElement(lg, "l")
            l.set("pos", v["pos"])
            l.text = v["lex"]
            lc = ET.SubElement(lg, "lc")
            lc.text = v["pos"]

            mg = ET.SubElement(e, "mg")
            for sense in v["senses"]:
                tg = ET.SubElement(mg, "tg")
                t = ET.SubElement(tg, "t")
                if "definition" in sense:
                    t.text = sense["definition"]
                    t.set("sources", "ALD")

        xml_string = ET.tostring(root)
        # pretty
        xml_string = minidom.parseString(xml_string).toprettyxml(indent="  ")

        with open("arpeng.xml", "w") as f:
            f.write(xml_string)
