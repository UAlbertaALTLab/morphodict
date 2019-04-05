import django
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Process, Queue
from threading import Lock
import math
import sqlite3
from sqlsp import SqlSP
import generate_forms_hfst as HFST
from fst_lookup import FST

# Hack for importing relative projects
import sys
import os
sys.path.append('../CreeDictionary')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CreeDictionary.settings")
django.setup()

# MUST BE IMPORTED AFTER sys.path.append
from API.admin import *
from API.models import *
from DictionaryParser import DictionaryParser

# The defaault number of processes that will be spawned for FST generation
DEFAULT_PROCESS_COUNT = 6


class DictionaryImporter:
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

    def __init__(self, fileName, sqlFileName, fstAnalyzerFileName, fstGeneratorFileName, hfstFileName, paradigmFolder, language):
        """
        Args:
            filename (str): The XML dictionary file name
            sqlFileName (str): The SQLITE3 DB fle name
            fstAnalyzerFileName (str): The FST Analyzer fomabin file
            fstGeneratorFileName (str): The FST Generator  formabin file
            paradigmFolder (str): The folder name that contains all paradigm files
            language (str): The language code for the dictionary
        """
        self.processCount = DEFAULT_PROCESS_COUNT
        self.fileName = fileName
        self.language = language
        self.sqlFileName = sqlFileName
        self.fstAnalyzerFileName = fstAnalyzerFileName
        self.fstGeneratorFileName = fstGeneratorFileName
        self.hfstFileName = hfstFileName
        self.paradigmFolder = paradigmFolder

    def _loadParadigmFiles(self):
        """
            Loads paradigm files into memory as strings in a dictionary
        """
        paradigmFiles = ["noun-nad", "noun-na", "noun-nid", "noun-ni",
                         "verb-ai", "verb-ii", "verb-ta", "verb-ti"]
        self.paradigmForms = dict()
        for filename in paradigmFiles:
            with open(self.paradigmFolder + filename + ".paradigm", "r") as file:
                content = file.read()
                # Split the content by --\n first and get the second half
                # then split by \n to get each form line
                # None will be removed using filter
                forms = list(filter(None, content.split("--\n")[1].split("\n")))
                self.paradigmForms[filename] = forms

    def parseSync(self, amount=10):
        """
            This is the synchronous version of parse
            No threads or processes will be created
            Should be used only for testing
        """
        self._loadParadigmFiles()
        print("Done Paradigm Loading")

        # Parse the XML file
        root = ET.parse(self.fileName).getroot()
        # Total element count in the XML file
        elementCount = len(root)

        # Queues
        lemmaQueue = Queue(elementCount * 2)
        definitionQueue = Queue(elementCount * 2 * 2)
        attributeQueue = Queue(elementCount * 2 * 10)
        inflectionQueue = Queue(elementCount * 2 * 100)
        inflectionFormQueue = Queue(elementCount * 2 * 100 * 10)
        finishedQueue = Queue(10)

        # Get the number of elements each process should handle
        chunkSize = elementCount / self.processCount

        print("Element Count: " + str(elementCount))

        # Init Process Fields
        self._initProcessFields(1, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue)

        initCounter = 0
        for element in root:
            if element.tag == "e":
                self._parseEntry(element)
            initCounter += 1
            if initCounter > amount:
                break

        self._fillDB(lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue)

        print("Done Parse")

    def parse(self):
        """
            Stars the parsing of XML dictionary, FST inflections generator and injects into SQL when done
        """
        self._loadParadigmFiles()
        print("Done Paradigm Loading")

        processCounter = 0
        processes = list()

        # Parse the XML file
        root = ET.parse(self.fileName).getroot()
        # Total element count in the XML file
        elementCount = len(root)

        # Queues for storing data that is ready to be inserted into SQL DB
        # Queues will be synchronized across threads and processes
        finishedQueue = Queue(self.processCount)
        lemmaQueue = Queue(elementCount * 2)
        definitionQueue = Queue(elementCount * 2 * 2)
        attributeQueue = Queue(elementCount * 2 * 10)
        inflectionQueue = Queue(elementCount * 2 * 100)
        inflectionFormQueue = Queue(elementCount * 2 * 100 * 10)

        # Get the number of elements each process should handle
        chunkSize = elementCount / self.processCount
        chunkSize = int(math.ceil(chunkSize))

        print("Element Count: " + str(elementCount))
        print("Process Chunk Size: " + str(chunkSize))

        # Create each process
        for i in range(self.processCount):
            # The indexes for current chunk
            lower = int(i * chunkSize)
            upper = int(min((i + 1) * chunkSize, elementCount))
            elements = root[lower: upper]
            # Create the process and pass queues to it
            process = Process(
                target=self._parseProcess,
                args=[
                    processCounter,
                    elements,
                    lemmaQueue,
                    attributeQueue,
                    inflectionQueue,
                    inflectionFormQueue,
                    definitionQueue,
                    finishedQueue])
            process.start()
            processes.append(process)
            print("Process " + str(processCounter) + " Started")
            processCounter += 1
        print("Done Process Init: " + str(processCounter))

        # Subprocecsses will not join unless queue is emptied
        # By using the finishedQueue, processes will pass their process ID to the queue
        # So that the parent/main process can know when to start processing queues
        finishedProcesses = list()
        while True:
            finishedProcess = finishedQueue.get(block=True)
            finishedProcesses.append(finishedProcess)
            if len(finishedProcesses) >= len(processes):
                break

        # All processes are finished, starts importing objects into DB
        self._fillDB(lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue)

        # Join the spawned processes
        for i in range(len(processes)):
            process = processes[i]
            process.join()
            print("Joined Process: " + str(i))
        print("Done Join")

    def _fillDB(self, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue):
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
        # Open connection
        conn = sqlite3.connect(self.sqlFileName)
        cur = conn.cursor()

        # Run SetUp.sql
        with open("SetUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            conn.commit()
        sqlSP = SqlSP(conn)
        print("Done SQL SetUp")

        lemmaIDDict = dict()
        lemmaContextDict = dict()
        while not lemmaQueue.empty():
            lemma = lemmaQueue.get()
            lemmaIDDict[lemma.id] = lemma
            if (lemma.context, lemma.type) not in lemmaContextDict:
                lemmaContextDict[(lemma.context, lemma.type)] = set()
            lemmaContextDict[(lemma.context, lemma.type)].add(lemma.id)

        inflectionIDDict = dict()
        inflectionContextDict = dict()
        while not inflectionQueue.empty():
            inflection = inflectionQueue.get()
            inflectionIDDict[inflection.id] = inflection
            if inflection.context not in inflectionContextDict:
                inflectionContextDict[inflection.context] = set()
            inflectionContextDict[inflection.context].add(inflection.id)
        print("Done Building Lemma and Inflection Dictionaries")

        # Insert Objects
        addedLemmaID = set()
        addedLemmaContext = set()
        for id, lemma in lemmaIDDict.items():
            if (lemma.context, lemma.type) not in addedLemmaContext:
                sqlSP.addWord(lemma.id, lemma.context, lemma.language, lemma.type)
                sqlSP.addLemma(lemma.id)
                addedLemmaID.add(lemma.id)
                addedLemmaContext.add((lemma.context, lemma.type))
        print("Done Inserting Lemma")

        while not attributeQueue.empty():
            attribute = attributeQueue.get()
            if attribute.lemmaID in addedLemmaID:
                sqlSP.addAttribute(attribute.id, attribute.name, attribute.lemmaID)
        print("Done Inserting Attribute")

        addedInflectionID = set()
        for id, inflection in inflectionIDDict.items():
            if inflection.lemmaID in addedLemmaID:
                sqlSP.addWord(inflection.id, inflection.context, inflection.language, inflection.type)
                sqlSP.addInflection(inflection.id, inflection.lemmaID)
                addedInflectionID.add(inflection.id)
        print("Done Inserting Inflection")

        while not inflectionFormQueue.empty():
            inflectionForm = inflectionFormQueue.get()
            if inflectionForm.inflectionID in addedInflectionID:
                sqlSP.addInflectionForm(inflectionForm.id, inflectionForm.name, inflectionForm.inflectionID)
        print("Done Inserting InflectionForm")

        while not definitionQueue.empty():
            definition = definitionQueue.get()
            if definition.wordID in addedLemmaID or definition.wordID in addedInflectionID:
                sqlSP.addDefinition(definition.id, definition.context, definition.source, definition.wordID)
            else:
                # Check wordID is lemma or inflection
                if definition.wordID in lemmaIDDict:
                    type = lemmaIDDict[definition.wordID].type
                    context = lemmaIDDict[definition.wordID].context
                    # Get list of lemma that has the same context and type as the not added lemma for this defintion
                    for lemmaID in lemmaContextDict[(context, type)]:
                        if lemmaID in addedLemmaID:
                            sqlSP.addDefinition(definition.id, definition.context, definition.source, lemmaID)
                            break
                elif definition.wordID in inflectionIDDict:
                    context = inflectionIDDict[definition.wordID].context
                    # Get list of inflection that has the same context as the not added inflection for this defintion
                    for inflectionID in inflectionContextDict[context]:
                        if inflectionID in addedInflectionID:
                            sqlSP.addDefinition(definition.id, definition.context, definition.source, inflectionID)
                            break
        print("Done Inserting Definition")

        conn.commit()

        # Run CleanUp.sql
        with open("CleanUp.sql", "r", encoding="utf-8-sig") as file:
            script = file.read()
            cur.executescript(script)
            # conn.commit()

        conn.commit()
        conn.close()
        print("Done SQL CleanUp")

    def _initProcessFields(self, processID, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue):
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
        # Process Specific Fields
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

    def _parseProcess(self, processID, elements, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue):
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
        # Init Process Fields
        self._initProcessFields(processID, lemmaQueue, attributeQueue, inflectionQueue, inflectionFormQueue, definitionQueue, finishedQueue)

        initCounter = 0
        with ThreadPoolExecutor(max_workers=1) as executor:
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
                    addCounter += 1
                    if addCounter % 25 == 0:
                        print("Process " + str(processID) + " Added: " + str(addCounter))
                except Exception as e:
                    print("Exception: ", e)

            print("Process " + str(processID) + " Done Adding: " + str(addCounter))
            finishedQueue.put(processID)

    def _getEntryID(self, type):
        """
            Get an ID for a type of object
            This is used for generating DB ID without collision
            Supports multiple processes by incrementing using the process count

            Args:
                type (Class but anything can be used): The type that the ID belongs to. Can be Lemma, Inflection, Word etc.
        """
        # Locks so no two processes/threads can edit entryIDDict
        self.entryIDLock.acquire()
        if type not in self.entryIDDict:
            # Initialize using the processID
            self.entryIDDict[type] = self.processID
        else:
            self.entryIDDict[type] += self.processCount
        entryID = self.entryIDDict[type]
        # Release Lock
        self.entryIDLock.release()
        return entryID

    def _parseEntry(self, entry):
        """
            Parse a single element in the XML dictionary and generate its inflections
            Lemma, Definition, Inlfection and InflectionForm objects will be
            Generated and put into the queues.

            Args:
                entry (ElementTree): The element to be parsed
            Returns:
                fstLemma (str): The lemma for the entry
        """
        # Get Lemma and FST Result
        lemmaResult = self.parser.parseLemma(entry)
        lemma = lemmaResult[0]
        wordContext = lemmaResult[1]
        bestFSTResult = lemmaResult[2]
        lemma.id = self._getEntryID(Word)
        self.lemmaQueue.put(lemma)

        # Parse Attributes
        if bestFSTResult is not None:
            attributes = self.parser.parseAttribute(lemma, bestFSTResult)
            for attribute in attributes:
                attribute.id = self._getEntryID(Attribute)
                self.attributeQueue.put(attribute)

        # Add definitions to current lemma if the entry is the lemma
        if wordContext == lemma.context:
            self._addDefinitions(lemma, entry)

        # If FST result does not exist for the word such as words without a type
        # Then skip inflection generation
        if bestFSTResult is not None:
            # Get Inflections
            inflectionResult = self.parser.getInflectionsHFST(lemma, bestFSTResult, self.hfstFileName)
            for inflectionPair in inflectionResult:
                inflection = inflectionPair[0]
                inflectionForms = inflectionPair[1]

                # Add ID to Inflection
                inflection.id = self._getEntryID(Word)
                self.inflectionQueue.put(inflection)
                for inflectionForm in inflectionForms:
                    # Add ID and FK of Inflection to InflectionForm
                    inflectionForm.id = self._getEntryID(InflectionForm)
                    inflectionForm.inflectionID = inflection.id
                    self.inflectionFormQueue.put(inflectionForm)

                if inflection.context == wordContext and inflection.context != lemma.context:
                    self._addDefinitions(inflection, entry)
        return lemma.context

    def _addDefinitions(self, word, entry):
        """
            Parse the definition and add it to the queue.
            Args:
                word (Word): The word the definition belongs to
                entry (ElementTree): XML that contains definitions
        """
        definitions = self.parser.parseDefinitions(word, entry)
        for definition in definitions:
            definition.id = self._getEntryID(Definition)
            self.definitionQueue.put(definition)


if __name__ == '__main__':

    mode = "normal"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

    importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3",
                                  "../CreeDictionary/API/fst/crk-descriptive-analyzer.fomabin", "../CreeDictionary/API/fst/crk-normative-generator.fomabin",
                                  "../CreeDictionary/API/fst/crk-normative-generator.hfstol",
                                  "../CreeDictionary/API/paradigm/", "crk")
    if mode == "test":
        importer.fileName = "../CreeDictionary/API/dictionaries/crkeng.test.xml"
        importer.sqlFileName = "../CreeDictionary/db.test.sqlite3"
        importer.parseSync(amount=50)
    elif mode == "normal":
        importer.parse()
    else:
        print("Unknown Mode")
