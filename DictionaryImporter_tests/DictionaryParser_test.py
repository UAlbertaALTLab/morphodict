import unittest
from unittest import mock
from DictionaryImporter import *
from DictionaryParser import *
from fst_lookup import FST
import json
import xml.etree.ElementTree as ET

"""
Tests should be run at the root folder of DictionaryImporter project
"""

class DictionaryParserTestCase(unittest.TestCase):
    # Shared fixture
    fstAnalyzerFileName = "../CreeDictionary/API/fst/crk-descriptive-analyzer.fomabin"
    fstGeneratorFileName = "../CreeDictionary/API/fst/crk-normative-generator.fomabin"
    hfstFileName = "../CreeDictionary/API/fst/crk-normative-generator.hfstol",
    fstAnalyzer = FST.from_file(fstAnalyzerFileName)
    fstGenerator = FST.from_file(fstGeneratorFileName)

    lemmaJSON = """
      <e>
        <lg>
          <l pos="N">mitâs</l>
          <lc>NDA-1</lc>
          <stem>-tâs-</stem>
        </lg>
        <mg>
          <tg xml:lang="eng">
            <t pos="N" sources="MD">Pants, jeans or trousers.</t>
          </tg>
        </mg>
        <mg>
          <tg xml:lang="eng">
            <t pos="N" sources="CW">pair of pants</t>
          </tg>
        </mg>
      </e>
    """

    pvJSON = """
      <e>
        <lg>
          <l pos="V">mêkwâ-nipâw</l>
          <lc></lc>
          <stem>-</stem>
        </lg>
        <mg>
          <tg xml:lang="eng">
            <t pos="V" sources="MD">He is sleeping right now.</t>
          </tg>
          <tg xml:lang="eng">
            <t pos="V" sources="CW">s/he sleeps, s/he is asleep</t>
          </tg>
        </mg>
      </e>
    """

    def setUp(self):
        self.importer = DictionaryImporter("../CreeDictionary/API/dictionaries/crkeng.xml", "../CreeDictionary/db.sqlite3",
                                           self.fstAnalyzerFileName, self.fstGeneratorFileName, self.hfstFileName,
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

    def test_parse_lemma(self):
        result = self.parser.parseLemma(ET.fromstring(self.pvJSON))
        lemma = result[0]
        wordContext = result[1]
        self.assertEqual(lemma.context, "nipâw")
        self.assertEqual(lemma.type, "V")
        self.assertEqual(wordContext, "mêkwâ-nipâw")

    def test_parse_lemma_pv(self):
        result = self.parser.parseLemma(ET.fromstring(self.lemmaJSON))
        lemma = result[0]
        wordContext = result[1]
        self.assertEqual(lemma.context, "mitâs")
        self.assertEqual(lemma.type, "N")
        self.assertEqual(wordContext, "mitâs")
