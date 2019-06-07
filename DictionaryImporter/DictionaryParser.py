from API.models import *
from API.admin import *
import generate_forms_hfst as HFST


class DictionaryParser:
    def __init__(self, paradigmForms, fstAnalyzer, fstGenerator, language):
        self.paradigmForms = paradigmForms
        self.fstAnalyzer = fstAnalyzer
        self.fstGenerator = fstGenerator
        self.language = language

    def _getParadigmFileName(self, wordType, fstResult):
        """
            Helper method for converting wordType and fstResult of a lemma to a paradigm file name
            Args:
                wordType (str): Lemma type, N, V (Does not handle IPV)
                fstResult (list): The FST result for the lemma. Should contain different attributes for such lemma (+A, +I, ++II etc).
            Returns:
                paradigmFilename (str):  The paradigm file name for lemma.
        """
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

    def parseLemma(self, entry):
        """
            Gets Lemma from an XML entry
            The entry can contain an inflection instead of a lemma
            FST will be used to get the inflection's lemma
            Returns:
                result (tuple): (lemma, wordContext, isLemma)
                                lemma (Lemma): The Lemma object parsed from the entry
                                wordContext (str): The orginal context that is stored inside the entry
                                bestFSTResult (list): Most probable FST result returned from FST Analyzer
                                                      Returns None when word has no type or FST cannot analyze
        """
        lemma = Lemma()
        # Get inner elements
        lg = entry.find("lg")
        l = lg.find("l")
        wordContext = l.text
        wordType = l.get("pos")
        # FST is used to make sure the word is a lemma otherwise generate its lemma
        fstResult = list(self.fstAnalyzer.analyze(wordContext))
        bestFSTResult = None
        # words without word type/pos should be treated as lemma without paradigm
        fstLemma = wordContext
        if len(fstResult) > 0 and wordType != "":
            bestFSTResult = fstResult[0]
            for item in bestFSTResult:
                if "+" not in item:
                    fstLemma = item

        # Init Lemma Object
        lemma.language = self.language
        lemma.context = fstLemma
        lemma.type = wordType

        return (lemma, wordContext, bestFSTResult)

    def parseDefinitions(self, word, entry):
        """
            Returns a list of Definition objects extracted from the XML
            Args:
                word (Word): The word that the definitions belong to
                entry (ElementTree): The XML that contains definitions
            Returns:
                definitions (list): List of Definition objects for word
        """
        definitions = list()
        for mg in entry.findall("mg"):
            for tg in mg.findall("tg"):
                for t in tg.findall("t"):
                    # Multiple sources for each definition. Such as CW MC with space in between
                    sources = t.get("sources").split(" ")
                    for source in sources:
                        # Init Definition object
                        definition = Definition()
                        definition.context = t.text
                        definition.source = source
                        definition.wordID = word.id
                        definitions.append(definition)
                        # print("Definition Added for: " + word.context)
        return definitions

    def parseAttribute(self, lemma, bestFSTResult):
        """
            Returns a list of Attribute objects extracted from the FST Result
            Args:
                lemma (Lemma): The lemma that the attributes belong to
                bestFSTResult (set): The FST result for the lemma
            Returns:
                attributes (list): List of Attribute objects for lemma
        """
        attributes = list()
        for attributeName in bestFSTResult:
            if attributeName == lemma.context:
                continue
            attribute = Attribute()
            attribute.name = attributeName.replace("+", "")
            attribute.lemmaID = lemma.id
            attributes.append(attribute)
        return attributes

    def getInflections(self, lemma, bestFSTResult):
        """
            Returns a list of Inflection objects with InflectionForm objects associated with each
            Args:
                lemma (Lemma): The lemma for the inflection
                bestFSTResult: The best FST result for the lemma
            Returns:
                inflections (list): Each item in the list is a tuple of (Inflecction, list()).
                                    The list contains all InflectionsForms of the Inflection.
        """
        inflections = list()
        paradigmFilename = self._getParadigmFileName(lemma.type, bestFSTResult)
        if paradigmFilename is not None:
            # Get paradigm
            forms = self.paradigmForms[paradigmFilename]
            # Generate Paradigms
            print("Generating Paradigms for: " + lemma.context)
            for form in forms:
                form = form.strip()
                # Skip comments
                if form.startswith("{#"):
                    continue
                # Replace placeholder with actual lemma
                generatorInput = form.replace("{{ lemma }}", lemma.context)
                # Generate inflection
                generatedResult = list(self.fstGenerator.generate(generatorInput))
                # generatedResult = ["asdasdas"]
                if len(generatedResult) < 1:
                    continue

                # Get the most probable inflection
                generatedInflection = generatedResult[0]

                # Init Inflection object
                inflection = Inflection()
                inflection.context = generatedInflection
                inflection.type = lemma.type
                inflection.language = self.language
                inflection.lemmaID = lemma.id

                # Get inflection forms
                form = form.replace("{{ lemma }}+", "")
                inflectionFormStrings = form.split("+")

                inflectionForms = list()
                # Init InflectionForm objects
                for inflectionFormString in inflectionFormStrings:
                    inflectionForm = InflectionForm()
                    inflectionForm.name = inflectionFormString
                    inflectionForms.append(inflectionForm)

                inflections.append((inflection, inflectionForms))
        return inflections

    def getInflectionsHFST(self, lemma, bestFSTResult, fstPath):
        """
        Returns a list of Inflection objects with InflectionForm objects associated with each
        Args:
            lemma (Lemma): The lemma for the inflection
            bestFSTResult: The best FST result for the lemma
        Returns:
            inflections (list): Each item in the list is a tuple of (Inflecction, list()).
                                The list contains all InflectionsForms of the Inflection.
        """
        inflections = list()
        paradigmFilename = self._getParadigmFileName(lemma.type, bestFSTResult)
        if paradigmFilename is not None:
            # Get paradigm
            forms = self.paradigmForms[paradigmFilename]
            # Generate Paradigms
            # print("Generating Paradigms for: " + lemma.context)
            generatorInputs = list()
            for form in forms:
                form = form.strip()
                # Skip comments
                if form.startswith("{#") or form == "":
                    continue
                # Replace placeholder with actual lemma
                generatorInput = form.replace("{{ lemma }}", lemma.context)
                generatorInputs.append(generatorInput)

            results = HFST.generate(generatorInputs, fst_path=fstPath)
            for form, generatedInflection in results.items():
                if len(generatedInflection) < 1:
                    continue
                # Init Inflection object
                inflection = Inflection()
                inflection.context = generatedInflection.pop()
                inflection.type = lemma.type
                inflection.language = self.language
                inflection.lemmaID = lemma.id

                # Get inflection forms
                form = form.replace(lemma.context + "+", "")
                inflectionFormStrings = form.split("+")

                inflectionForms = list()
                # Init InflectionForm objects
                for inflectionFormString in inflectionFormStrings:
                    inflectionForm = InflectionForm()
                    inflectionForm.name = inflectionFormString
                    inflectionForms.append(inflectionForm)

                inflections.append((inflection, inflectionForms))
        return inflections
