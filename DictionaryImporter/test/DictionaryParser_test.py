import unittest
from unittest import mock
from DictionaryParser import *
from DictionaryImporter import *
from fst_lookup import FST
import json

"""
Tests should be run at the root folder of DictionaryImporter project
"""


class DictionaryImporrterTestCase(unittest.TestCase):
    # Shared fixture
    fstAnalyzerFileName = "../CreeDictionary/API/fst/crk-analyzer.fomabin.gz"
    fstGeneratorFileName = "../CreeDictionary/API/fst/crk-generator.fomabin.gz"
    fstAnalyzer = FST.from_file(fstAnalyzerFileName)
    fstGenerator = FST.from_file(fstGeneratorFileName)

    def setUp(self):
        self.importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3",
                                           self.fstAnalyzerFileName, self.fstGeneratorFileName,
                                           "../CreeDictionary/API/paradigm/", "crk")
        self.importer._loadParadigmFiles()
        self.parser = DictionaryParser(self.importer.paradigmForms, self.fstAnalyzer, self.fstGenerator, "crk")

    def tearDown(self):
        self.importer = None
        self.parser = None

    def test_get_paradigm_file_name(self):
        fileName = self.parser._getParadigmFileName("N", {"+I", "+D"})
        self.assertEqual(fileName, "noun-nid")
        fileName = self.parser._getParadigmFileName("N", {"+I"})
        self.assertEqual(fileName, "noun-ni")

    def test_parse_definitions(self):
        pass
