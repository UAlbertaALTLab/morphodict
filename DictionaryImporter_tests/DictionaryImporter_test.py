import unittest
from os import path
from unittest import mock
import xml.etree.ElementTree as ET

# from DictionaryImporter.DictionaryImporter import *

"""
Tests should be run at the root folder of DictionaryImporter project
"""

FILE_DIR = path.dirname(__file__)


# class DictionaryImporterTestCase(unittest.TestCase):
#     def setUp(self):
#         self.importer = DictionaryImporter(
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'API', 'dictionaries', 'crkeng.xml'),
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'db.sqlite3'),
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'API', 'fst',
#                       'crk-descriptive-analyzer.fomabin'),
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'API', 'fst',
#                       'crk-normative-generator.fomabin'),
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'API', 'fst',
#                       'crk-normative-generator.hfstol'),
#             path.join(FILE_DIR, '..', 'CreeDictionary', 'API',
#                       'paradigm'), 'crk')
#
#         self.importer.processCount = 0
#
#     def test_get_entry_id(self):
#         # Mock FST.from_file() to speed up test
#         with mock.patch('DictionaryImporter.FST.from_file') as mockFST:
#             mockFST.return_value = None
#             self.importer.processCount = 8
#             self.importer._loadParadigmFiles()
#             self.importer._initProcessFields(3, None, None, None, None, None, None)
#             self.assertIs(self.importer._getEntryID(Word), 3)
#             self.assertIs(self.importer._getEntryID(Word), 11)
#             self.assertIs(self.importer._getEntryID(Word), 19)
#             self.assertIs(self.importer._getEntryID(Lemma), 3)
#             self.assertIs(self.importer._getEntryID(Lemma), 11)
#             self.assertIs(self.importer._getEntryID(Inflection), 3)

def testET():
    return ET.parse(path.join(FILE_DIR, 'fixtures', 'crkeng_test.xml'))
