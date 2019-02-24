import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Process, Queue
from threading import Lock
import math
import sqlite3
from sqlsp import SqlSP

#Hack for importing relative projects
import sys
import os
sys.path.append('../CreeDictionary')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CreeDictionary.settings")
import django
django.setup()

from API.models import *
from API.admin import *

from fst_lookup import FST


DEFAULT_PROCESS_COUNT = 6

class DictionaryImporter:
    def __init__(self, filename, sqlFileName, fstAnalyzerFileName, fstGeneratorFileName, paradigmFolder, language):
        self.processCount = DEFAULT_PROCESS_COUNT
        self.filename = filename
        self.language = language
        self.sqlFileName = sqlFileName
        self.fstAnalyzerFileName = fstAnalyzerFileName
        self.fstGeneratorFileName = fstGeneratorFileName
        self.paradigmFolder = paradigmFolder
        self.loadParadigmFiles()
        print("Done Paradigm Loading")


    def loadParadigmFiles(self):
        paradigmFiles = ["noun-nad", "noun-na", "noun-nid", "noun-ni",
                         "verb-ai", "verb-ii", "verb-ta", "verb-ti"]
        self.paradigmForms = dict()
        for filename in paradigmFiles:
            with open(self.paradigmFolder + filename + ".paradigm", "r") as file:
                content = file.read()
                forms = list(filter(None, content.split("--\n")[1].split("\n")))
                self.paradigmForms[filename] = forms

    def parse(self):
        processCounter = 0
        processes = list()

        root = ET.parse(self.filename).getroot()
        elementCount = len(root)
        
        finishedQueue = Queue(self.processCount)
        lemmaQueue = Queue(elementCount * 2)
        definitionQueue = Queue(elementCount * 2 * 2)
        attributeQueue = Queue(elementCount * 2 * 10)
        inflectionQueue = Queue(elementCount * 2 * 100)
        inflectionFormQueue = Queue(elementCount * 2 * 100 * 10)

        chunkSize = elementCount / self.processCount
        chunkSize = int(math.ceil(chunkSize))
        
        print("Element Count: " + str(elementCount))
        print("Process Chunk Size: " + str(chunkSize))

        for i in range(self.processCount):
        #for i in range(6):
            lower = int(i * chunkSize)
            upper = int(min((i + 1) * chunkSize, elementCount))
            elements = root[lower: upper]
            process = Process(target=self._parseProcess, args=[processCounter, elements, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue])
            process.start()
            processes.append(process)
            print("Process " + str(processCounter) + " Started")
            processCounter += 1
        print("Done Process Init: " + str(processCounter))

        #Subprocecsses will not join unless queue is emptied
        finishedProcesses = list()
        while True:
            finishedProcess = finishedQueue.get(block=True)
            finishedProcesses.append(finishedProcess)
            if len(finishedProcesses) >= len(processes):
                break

        self._fillDB(lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue)

        for i in range(len(processes)):
            process = processes[i]
            process.join()
            print("Joined Process: " + str(i))
        print("Done Join")


    def _fillDB(self, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue):
        conn = sqlite3.connect(self.sqlFileName)
        cur = conn.cursor()
        
        with open("SetUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            conn.commit()
        sqlSP = SqlSP(conn)
        print("Done SQL SetUp")
        
        while not lemmaQueue.empty():
            lemma = lemmaQueue.get()
            sqlSP.addWord(lemma.id, lemma.context, lemma.language, lemma.type)
            sqlSP.addLemma(lemma.id)
        print("Done Inserting Lemma")

        while not attributeQueue.empty():
            attribute = attributeQueue.get()
            #sqlSP.addAttribute(attribute.id, attribute.name, attribute.lemmaID)
        print("Done Inserting Attribute")

        while not inflectionQueue.empty():
            inflection = inflectionQueue.get()
            sqlSP.addWord(inflection.id, inflection.context, inflection.language, inflection.type)
            sqlSP.addInflection(inflection.id, inflection.lemmaID)
        print("Done Inserting Inflection")
            

        while not inflectionFormQueue.empty():
            inflectionForm = inflectionFormQueue.get()
            sqlSP.addInflectionForm(inflectionForm.id, inflectionForm.name, inflectionForm.inflectionID)
        print("Done Inserting InflectionForm")

        while not definitionQueue.empty():
            definition = definitionQueue.get()
            sqlSP.addDefinition(definition.id, definition.context, definition.source, definition.wordID)
        print("Done Inserting Definition")
        
        conn.commit();

        with open("CleanUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            #conn.commit()
            
        print("Done SQL CleanUp")

    def _parseProcess(self, processID, elements, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue):
        #Process Specific Vars
        self.fstAnalyzer = FST.from_file(self.fstAnalyzerFileName)
        self.fstGenerator = FST.from_file(self.fstGeneratorFileName)
        print("Process " + str(processID) + " Done FST Loading")
        self.processID = processID
        self.lemmaQueue = lemmaQueue
        self.attributeQueue = attributeQueue
        self.inflectionQueue = inflectionQueue
        self.inflectionFormQueue = inflectionFormQueue
        self.definitionQueue = definitionQueue
        self.entryIDLock = Lock()
        self.entryIDDict = dict()

        initCounter = 0
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = list()
            for element in elements:
                if element.tag == "e":
                    futures.append(executor.submit(self._parseEntry, element))
                    initCounter += 1
                    if initCounter % 100 == 0:
                        print("Process " + str(processID) + " Initialized: " + str(initCounter))
            print("Process " + str(processID) + " Done Init: " + str(initCounter))

            addCounter = 0
            for future in as_completed(futures):
                try:
                    lemma = future.result()
                    addCounter += 1;
                    if addCounter % 25 == 0:
                        print("Process " + str(processID) + " Added: " + str(addCounter))
                except Exception as e:
                    print("Exception: ", e)
                
            print("Process " + str(processID) + " Done Adding: " + str(addCounter))
            finishedQueue.put(processID)

    def _getEntryID(self, type):
        self.entryIDLock.acquire()
        if type not in self.entryIDDict:
            self.entryIDDict[type] = self.processID
        else:
            self.entryIDDict[type] += self.processCount
        entryID = self.entryIDDict[type]
        self.entryIDLock.release()
        return entryID

    def _parseEntry(self, entry):
        lemma = Lemma()
        definitions = list()

        #Lemma Check
        lg = entry.find("lg")
        l = lg.find("l")
        wordContext = l.text
        wordType = l.get("pos")
        fstResult = list(self.fstAnalyzer.analyze(wordContext))
        bestFSTResult = None
        # words without word type/pos should be treated as lemma without paradigm
        if len(fstResult) > 0 and wordType != "":
            bestFSTResult = fstResult[0]
            fstLemma = bestFSTResult[0]
        else:
            fstLemma = wordContext
        isLemma = wordContext == fstLemma

        lemma.language = self.language
        lemma.context = fstLemma
        lemma.type = wordType
        lemma.id = self._getEntryID(Word)
        self.lemmaQueue.put(lemma)
        
        if isLemma:
            self._parseDefinitions(lemma, entry)

        if bestFSTResult != None:
            paradigmFilename = self._getParadigmFilename(wordType, bestFSTResult)
            if paradigmFilename != None:
                forms = self.paradigmForms[paradigmFilename]
                # Generate Paradigms
                #print("Generating Paradigms for: " + fstLemma)
                for form in forms:
                    form = form.strip()
                    if form.startswith("{#"):
                        continue
                    generatorInput = form.replace("{{ lemma }}", fstLemma)
                    generatedResult = list(self.fstGenerator.generate(generatorInput))
                    #generatedResult = ["asdasdas"]
                    if len(generatedResult) < 1:
                        continue
                    
                    generatedInflection = generatedResult[0]

                    inflection = Inflection()
                    inflection.context = generatedInflection
                    inflection.type = wordType
                    inflection.language = self.language
                    inflection.lemmaID = lemma.id
                    inflection.id = self._getEntryID(Word)
                    self.inflectionQueue.put(inflection)
                    
                    form = form.replace("{{ lemma }}+", "")
                    inflectionFormStrings = form.split("+")

                    for inflectionFormString in inflectionFormStrings:
                        inflectionForm = InflectionForm()
                        inflectionForm.name = inflectionFormString
                        inflectionForm.inflectionID = inflection.id
                        self.inflectionFormQueue.put(inflectionForm)

                    if generatedInflection == wordContext and generatedInflection != fstLemma:
                        self._parseDefinitions(inflection, entry)
        return fstLemma

        
    def _getParadigmFilename(self, wordType, fstResult):
            paradigmFilename = None
            if wordType == "N":
                if "+A" in fstResult and "+D" in fstResult:
                    paradigmFilename = "noun-nad"
                elif "+A" in fstResult:
                    paradigmFilename = "noun-na"
                elif "+I" in fstResult and "+D" in fstResult:
                    paradigmFilename = "noun-nid"
                elif "+I" in fstResult:
                    paradigmFilename = "noun-ni"
            elif wordType == "V":
                if "+AI" in fstResult:
                    paradigmFilename = "verb-ai"
                elif "+II" in fstResult:
                    paradigmFilename = "verb-ii"
                elif "+TA" in fstResult:
                    paradigmFilename = "verb-ta"
                elif "+TI" in fstResult:
                    paradigmFilename = "verb-ti"
            return paradigmFilename

    def _parseDefinitions(self, word, entry):
        for mg in entry.findall("mg"):
            for tg in mg.findall("tg"):
                for t in tg.findall("t"):
                    sources = t.get("sources").split(" ")
                    for source in sources:
                        definition = Definition()
                        definition.context = t.text
                        definition.source = source
                        definition.wordID = word.id
                        definition.id = self._getEntryID(Definition)
                        self.definitionQueue.put(definition)
                        #print("Definition Added for: " + word.context)

if __name__ == '__main__':
    importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3", 
                                  "../CreeDictionary/API/dictionaries/crk-analyzer.fomabin.gz", "../CreeDictionary/API/dictionaries/crk-generator.fomabin.gz", 
                                  "../CreeDictionary/API/paradigm/", "crk")
    importer.parse()