import xml.etree.ElementTree as ET

#Hack for importing relative projects
import sys
import os
sys.path.append('../CreeDictionary')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CreeDictionary.settings")

import django
django.setup()

from API.models import *
from API.admin import *

from django.db import transaction

class DictionaryImporter:
    def __init__(self, filename, language):
        self.filename = filename
        self.language = language

    #Single Transaction
    @transaction.atomic
    def parse(self):
        counter = 0
        root = ET.parse(self.filename).getroot()
        for element in root:
            if element.tag == "e":
                self.parseEntry(element)
                counter += 1
                if counter % 100 == 0:
                    print("Added: " + str(counter))
        print("Done: " + str(counter))

    def parseEntry(self, entry):
        word = Word()
        definitions = list()
        
        #Lemma
        word.language = self.language
        lg = entry.find("lg")
        l = lg.find("l")
        word.context = l.text
        word.type = l.get("pos")
        word.save()

        #Definitions
        for tg in entry.findall("tg"):
            for t in tg.findall("t"):
                sources = t.get("sources").split(" ")
                for source in sources:
                    definition = Definition()
                    definition.context = t.text
                    definition.source = source
                    definition.fk_word = word

importer = DictionaryImporter("Dictionaries/crkeng.xml", "crk")
importer.parse()

'''
word = Word()
word.context = "B"
word.language = "en-US"
word.save()

d1 = Definition()
d1.context = "B Definition 1"
d1.source = "BW"
d1.fk_word = word
d1.save()

d2 = Definition()
d2.context = "B Definition 2"
d2.source = "CW"
d2.fk_word = word
d2.save()


definitions = Definition.objects.filter(fk_word = word)

for definition in definitions:
    print(definition.context)
'''