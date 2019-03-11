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
from DictionaryParser import DictionaryParser

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
        This is the synchronous version of parse
        No threads or processes will be created
        Should be used only for testing
    """
    def parseSync(self):
        self._loadParadigmFiles()
        print("Done Paradigm Loading")

        #Parse the XML file
        root = ET.parse(self.fileName).getroot()
        #Total element count in the XML file
        elementCount = len(root)
        
        #Queues
        lemmaQueue = Queue(elementCount * 2)
        definitionQueue = Queue(elementCount * 2 * 2)
        attributeQueue = Queue(elementCount * 2 * 10)
        inflectionQueue = Queue(elementCount * 2 * 100)
        inflectionFormQueue = Queue(elementCount * 2 * 100 * 10)
        finishedQueue = Queue(10)

        #Get the number of elements each process should handle
        chunkSize = elementCount / self.processCount
        
        print("Element Count: " + str(elementCount))

        #Init Process Fields
        self._initProcessFields(1, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue)

        initCounter = 0
        for element in root:
            if element.tag == "e":
                self._parseEntry(element)

        self._fillDB(lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue)

        print("Done Parse")


    """
        Stars the parsing of XML dictionary, FST inflections generator and injects into SQL when done
    """
    def parse(self):
        self._loadParadigmFiles()
        print("Done Paradigm Loading")

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
 
        while not attributeQueue.empty():
            attribute = attributeQueue.get()
            sqlSP.addAttribute(attribute.id, attribute.name, attribute.lemmaID)
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
        Initialized all fields that uniquely belong to the current process
        Args:
            processID (int): The process ID that is assigned to the process
            lemmaQueue (Queue)
            attributeQueue (Queue)
            inflectionQueue (Queue)
            inflectionFormQueue (Queue)
            definitionQueue (Queue)
            finishedQueue (Queue)
    """
    def _initProcessFields(self, processID, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue):
        #Process Specific Fields
        self.fstAnalyzer = FST.from_file(self.fstAnalyzerFileName)
        self.fstGenerator = FST.from_file(self.fstGeneratorFileName)
        print("Process " + str(processID) + " Done FST Loading")
        self.parser = DictionaryParser(self.paradigmForms, self.fstAnalyzer, self.fstGenerator, self.language)
        self.processID = processID
        self.lemmaQueue = lemmaQueue
        self.attributeQueue = attributeQueue
        self.inflectionQueue = inflectionQueue
        self.inflectionFormQueue = inflectionFormQueue
        self.definitionQueue = definitionQueue
        self.entryIDLock = Lock()
        self.entryIDDict = dict()

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
        #Init Process Fields
        self._initProcessFields(processID, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue)

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
        #Get Lemma and FST Result
        lemmaResult = self.parser.parseLemma(entry)
        lemma = lemmaResult[0]
        wordContext = lemmaResult[1]
        bestFSTResult = lemmaResult[2]
        lemma.id = self._getEntryID(Word)
        self.lemmaQueue.put(lemma)

        # Parse Attributes
        if bestFSTResult != None:
            attributes = self.parser.parseAttribute(lemma, bestFSTResult)
            for attribute in attributes:
                attribute.id = self._getEntryID(Attribute)
                self.attributeQueue.put(attribute)
        
        #Add definitions to current lemma if the entry is the lemma
        if wordContext == lemma.context:
            self._addDefinitions(lemma, entry)

        #If FST result does not exist for the word such as words without a type
        #Then skip inflection generation
        if bestFSTResult != None:
            # Get Inflections
            inflectionResult = self.parser.getInflections(lemma, bestFSTResult)
            for inflectionPair in inflectionResult:
                inflection = inflectionPair[0]
                inflectionForms = inflectionPair[1]

                #Add ID to Inflection
                inflection.id = self._getEntryID(Word)
                self.inflectionQueue.put(inflection)
                for inflectionForm in inflectionForms:
                    #Add ID and FK of Inflection to InflectionForm
                    inflectionForm.id = self._getEntryID(InflectionForm)
                    inflectionForm.inflectionID = inflection.id
                    self.inflectionFormQueue.put(inflectionForm)
                    
                if inflection.context == wordContext and inflection.context != lemma.context:
                    self._addDefinitions(inflection, entry)
        return lemma.context

    """
        Parse the definition and add it to the queue.
        Args:
            word (Word): The word the definition belongs to
            entry (ElementTree): XML that contains definitions
    """
    def _addDefinitions(self, word, entry):
        definitions = self.parser.parseDefinitions(word, entry)
        for definition in definitions:
            definition.id = self._getEntryID(Definition)
            self.definitionQueue.put(definition)

if __name__ == '__main__':
    importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3", 
                                  "../CreeDictionary/API/dictionaries/crk-analyzer.fomabin.gz", "../CreeDictionary/API/dictionaries/crk-generator.fomabin.gz", 
                                  "../CreeDictionary/API/paradigm/", "crk")
    importer.parseSync()
    #importer.parse()