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

# The defaault number of processes that will be spawned for FST generation
DEFAULT_PROCESS_COUNT = 6

"""
    This class is used to import XML dictionary into a SQLite3 Database using 
    FST generator to generate inflections for each lemma.
    The generation is multithreaded and multiprocessed.
    Multiple processes are used due the the limitation of 
    Python's GIL(GlobalInterpreterLock) which means all threads in 
    A single process will be ran on the same CPU core
    
    This class can be scaled with more CPU resources.

    In most cases the bottleneck should be CPU with memeory useage around 6G.

    The field processCount should be changed depending on number of cores a CPU
    has before running parse()
"""
class DictionaryImporter:
    """
    Args:
        filename (str): The XML dictionary file name
        sqlFileName (str): The SQLITE3 DB fle name
        fstAnalyzerFileName (str): The FST Analyzer fomabin file
        fstGeneratorFileName (str): The FST Generator  formabin file
        paradigmFolder (str): The folder name that contains all paradigm files
        language (str): The language code for the dictionary
    """
    def __init__(self, fileName, sqlFileName, fstAnalyzerFileName, fstGeneratorFileName, paradigmFolder, language):
        self.processCount = DEFAULT_PROCESS_COUNT
        self.fileName = fileName
        self.language = language
        self.sqlFileName = sqlFileName
        self.fstAnalyzerFileName = fstAnalyzerFileName
        self.fstGeneratorFileName = fstGeneratorFileName
        self.paradigmFolder = paradigmFolder
        self._loadParadigmFiles()
        print("Done Paradigm Loading")

    """
        Loads paradigm files into memory as strings in a dictionary
    """
    def _loadParadigmFiles(self):
        paradigmFiles = ["noun-nad", "noun-na", "noun-nid", "noun-ni",
                         "verb-ai", "verb-ii", "verb-ta", "verb-ti"]
        self.paradigmForms = dict()
        for filename in paradigmFiles:
            with open(self.paradigmFolder + filename + ".paradigm", "r") as file:
                content = file.read()
                #Split the content by --\n first and get the second half
                #then split by \n to get each form line
                #None will be removed using filter
                forms = list(filter(None, content.split("--\n")[1].split("\n")))
                self.paradigmForms[filename] = forms

    """
        Stars the parsing of XML dictionary, FST inflections generator and injects into SQL when done
    """
    def parse(self):
        processCounter = 0
        processes = list()

        #Parse the XML file
        root = ET.parse(self.fileName).getroot()
        #Total element count in the XML file
        elementCount = len(root)
        
        #Queues for storing data that is ready to be inserted into SQL DB
        #Queues will be synchronized across threads and processes
        finishedQueue = Queue(self.processCount)
        lemmaQueue = Queue(elementCount * 2)
        definitionQueue = Queue(elementCount * 2 * 2)
        attributeQueue = Queue(elementCount * 2 * 10)
        inflectionQueue = Queue(elementCount * 2 * 100)
        inflectionFormQueue = Queue(elementCount * 2 * 100 * 10)

        #Get the number of elements each process should handle
        chunkSize = elementCount / self.processCount
        chunkSize = int(math.ceil(chunkSize))
        
        print("Element Count: " + str(elementCount))
        print("Process Chunk Size: " + str(chunkSize))

        #Create each process
        for i in range(self.processCount):
            #The indexes for current chunk
            lower = int(i * chunkSize)
            upper = int(min((i + 1) * chunkSize, elementCount))
            elements = root[lower: upper]
            #Create the process and pass queues to it
            process = Process(target=self._parseProcess, args=[processCounter, elements, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue])
            process.start()
            processes.append(process)
            print("Process " + str(processCounter) + " Started")
            processCounter += 1
        print("Done Process Init: " + str(processCounter))

        #Subprocecsses will not join unless queue is emptied
        #By using the finishedQueue, processes will pass their process ID to the queue
        #So that the parent/main process can know when to start processing queues
        finishedProcesses = list()
        while True:
            finishedProcess = finishedQueue.get(block=True)
            finishedProcesses.append(finishedProcess)
            if len(finishedProcesses) >= len(processes):
                break

        #All processes are finished, starts importing objects into DB
        self._fillDB(lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue)

        #Join the spawned processes
        for i in range(len(processes)):
            process = processes[i]
            process.join()
            print("Joined Process: " + str(i))
        print("Done Join")

    """
        Fills the DB with objects in the queues
        Runs SetUp.sql before inserting and CleanUp when done
        SetUp should remove indexes and disable FK to speed up insert
        CleanUp should regenerate indexes

        Agrs:
            lemmaQueue (Queue)
            attributeQueue (Queue)
            inflectionQueue (Queue)
            inflectionFormQueue (Queue)
            definitionQueue (Queue)

    """
    def _fillDB(self, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue):
        #Open connection
        conn = sqlite3.connect(self.sqlFileName)
        cur = conn.cursor()
        
        #Run SetUp.sql
        with open("SetUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            conn.commit()
        sqlSP = SqlSP(conn)
        print("Done SQL SetUp")
        
        #Insert Objects

        while not lemmaQueue.empty():
            lemma = lemmaQueue.get()
            sqlSP.addWord(lemma.id, lemma.context, lemma.language, lemma.type)
            sqlSP.addLemma(lemma.id)
        print("Done Inserting Lemma")

        #TODO Add Attribute Parsing 
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

        #Run CleanUp.sql
        with open("CleanUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            #conn.commit()
            
        print("Done SQL CleanUp")

    """
        This should be the entry point when a new process is spawned
        Threads will be spawned to fully utilize the process
        Args:
            processID (int): The process ID that is assigned to the process
            elements (ElementTree): XML elements that contains lemma and inflection
            lemmaQueue (Queue)
            attributeQueue (Queue)
            inflectionQueue (Queue)
            inflectionFormQueue (Queue)
            definitionQueue (Queue)
            finishedQueue (Queue)
            
    """
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
    """
        Get an ID for a type of object
        This is used for generating DB ID without collision
        Supports multiple processes by incrementing using the process count

        Args:
            type (Class but anything can be used): The type that the ID belongs to. Can be Lemma, Inflection, Word etc.
    """
    def _getEntryID(self, type):
        #Locks so no two processes/threads can edit entryIDDict
        self.entryIDLock.acquire()
        if type not in self.entryIDDict:
            #Initialize using the processID
            self.entryIDDict[type] = self.processID
        else:
            self.entryIDDict[type] += self.processCount
        entryID = self.entryIDDict[type]
        #Release Lock
        self.entryIDLock.release()
        return entryID

    """
        Parse a single element in the XML dictionary and generate its inflections
        Lemma, Definition, Inlfection and InflectionForm objects will be
        Generated and put into the queues.

        Args:
            entry (ElementTree): The element to be parsed
        Returns:
            fstLemma (str): The lemma for the entry
    """
    def _parseEntry(self, entry):
        lemma = Lemma()
        definitions = list()

        #Lemma Check
        lg = entry.find("lg")
        l = lg.find("l")
        wordContext = l.text
        wordType = l.get("pos")
        #FST is used to make sure the word is a lemma otherwise generate its lemma
        fstResult = list(self.fstAnalyzer.analyze(wordContext))
        bestFSTResult = None
        # words without word type/pos should be treated as lemma without paradigm
        if len(fstResult) > 0 and wordType != "":
            bestFSTResult = fstResult[0]
            fstLemma = bestFSTResult[0]
        else:
            fstLemma = wordContext
        isLemma = wordContext == fstLemma

        #Init Lemma Object
        lemma.language = self.language
        lemma.context = fstLemma
        lemma.type = wordType
        lemma.id = self._getEntryID(Word)
        self.lemmaQueue.put(lemma)
        
        #Add definitions to current lemma if the entry is the lemma
        if isLemma:
            self._addDefinitions(lemma, entry)

        #If FST result does not exist for the word such as words without a type
        #Then skip inflection generation
        if bestFSTResult != None:
            paradigmFilename = self._getParadigmFileName(wordType, bestFSTResult)
            if paradigmFilename != None:
                #Get paradigm
                forms = self.paradigmForms[paradigmFilename]
                # Generate Paradigms
                #print("Generating Paradigms for: " + fstLemma)
                for form in forms:
                    form = form.strip()
                    #Skip comments
                    if form.startswith("{#"):
                        continue
                    #Replace placeholder with actual lemma
                    generatorInput = form.replace("{{ lemma }}", fstLemma)
                    #Generate inflection
                    generatedResult = list(self.fstGenerator.generate(generatorInput))
                    #generatedResult = ["asdasdas"]
                    if len(generatedResult) < 1:
                        continue
                    
                    #Get the most probable inflection
                    generatedInflection = generatedResult[0]

                    #Init Inflection object
                    inflection = Inflection()
                    inflection.context = generatedInflection
                    inflection.type = wordType
                    inflection.language = self.language
                    inflection.lemmaID = lemma.id
                    inflection.id = self._getEntryID(Word)
                    self.inflectionQueue.put(inflection)
                    
                    #Get inflection forms
                    form = form.replace("{{ lemma }}+", "")
                    inflectionFormStrings = form.split("+")

                    #Init InflectionForm objects
                    for inflectionFormString in inflectionFormStrings:
                        inflectionForm = InflectionForm()
                        inflectionForm.name = inflectionFormString
                        inflectionForm.inflectionID = inflection.id
                        self.inflectionFormQueue.put(inflectionForm)

                    if generatedInflection == wordContext and generatedInflection != fstLemma:
                        self._addDefinitions(inflection, entry)
        return fstLemma

    """
        Parse the definition and add it to the queue.
        Args:
            word (Word): The word the definition belongs to
            entry (ElementTree): XML that contains definitions
    """
    def _addDefinitions(self, word, entry):
        definitions = self._parseDefinitions(word, entry)
        for definition in definitions:
            self.definitionQueue.put(definition)

    """
        Helper method for converting wordType and fstResult of a lemma to a paradigm file name
        Args:
            wordType (str): Lemma type, N, V (Does not handle IPV)
            fstResult (list): The FST result for the lemma. Should contain different attributes for such lemma (+A, +I, ++II etc).
        Returns:
            paradigmFilename (str):  The paradigm file name for lemma.
    """
    def _getParadigmFileName(self, wordType, fstResult):
            paradigmFileName = None
            if wordType == "N":
                if "+A" in fstResult and "+D" in fstResult:
                    paradigmFileName = "noun-nad"
                elif "+A" in fstResult:
                    paradigmFileName = "noun-na"
                elif "+I" in fstResult and "+D" in fstResult:
                    paradigmFileName = "noun-nid"
                elif "+I" in fstResult:
                    paradigmFileName = "noun-ni"
            elif wordType == "V":
                if "+AI" in fstResult:
                    paradigmFileName = "verb-ai"
                elif "+II" in fstResult:
                    paradigmFileName = "verb-ii"
                elif "+TA" in fstResult:
                    paradigmFileName = "verb-ta"
                elif "+TI" in fstResult:
                    paradigmFileName = "verb-ti"
            return paradigmFileName

    """
        Returns a list of Definition objects extracted from the XML
        Args:
            word (Word): The word that the definitions belong to
            entry (ElementTree): The XML that contains definitions
        Returns:
            definitions (list): List of Definition objects for word
    """
    def _parseDefinitions(self, word, entry):
        definitions = list()
        for mg in entry.findall("mg"):
            for tg in mg.findall("tg"):
                for t in tg.findall("t"):
                    #Multiple sources for each definition. Such as CW MC with space in between
                    sources = t.get("sources").split(" ")
                    for source in sources:
                        #Init Definition object
                        definition = Definition()
                        definition.context = t.text
                        definition.source = source
                        definition.wordID = word.id
                        definition.id = self._getEntryID(Definition)
                        definitions.append(definition)
                        #print("Definition Added for: " + word.context)
        return definitions

if __name__ == '__main__':
    importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3", 
                                  "../CreeDictionary/API/dictionaries/crk-analyzer.fomabin.gz", "../CreeDictionary/API/dictionaries/crk-generator.fomabin.gz", 
                                  "../CreeDictionary/API/paradigm/", "crk")
    importer.parse()