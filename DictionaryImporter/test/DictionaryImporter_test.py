import unittest
from unittest import mock
from DictionaryImporter import *
import json

"""
Tests should be run at the root folder of DictionaryImporter project
"""


class DictionaryImporterTestCase(unittest.TestCase):
    def setUp(self):
        self.importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3",
                                           "../CreeDictionary/API/fst/crk-descriptive-analyzer.fomabin",
                                           "../CreeDictionary/API/fst/crk-normative-generator.fomabin",
                                           "../CreeDictionary/API/fst/crk-normative-generator.hfstol",
                                           "../CreeDictionary/API/paradigm/", "crk")
        self.importer.processCount = 0

    def tearDown(self):
        self.importer = None

    def test_get_entry_id(self):
        # Mock FST.from_file() to speed up test
        with mock.patch('DictionaryImporter.FST.from_file') as mockFST:
            mockFST.return_value = None
            self.importer.processCount = 8
            self.importer._loadParadigmFiles()
            self.importer._initProcessFields(3, None, None, None, None, None, None)
            self.assertIs(self.importer._getEntryID(Word), 3)
            self.assertIs(self.importer._getEntryID(Word), 11)
            self.assertIs(self.importer._getEntryID(Word), 19)
            self.assertIs(self.importer._getEntryID(Lemma), 3)
            self.assertIs(self.importer._getEntryID(Lemma), 11)
            self.assertIs(self.importer._getEntryID(Inflection), 3)
