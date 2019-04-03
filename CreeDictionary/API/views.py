from django.shortcuts import render
from django.http import HttpResponse
from fst_lookup import FST
from django.conf import settings
from API.models import *
import os
from urllib.parse import unquote
import unicodedata
import json
from django.forms.models import model_to_dict
import API.datafetch as datafetch
from cree_sro_syllabics import syllabics2sro

fstAnalyzer = FST.from_file(os.path.join(settings.BASE_DIR, "API/fst/crk-descriptive-analyzer.fomabin"))
# fstGenerator = FST.from_file(os.path.join(settings.BASE_DIR, "API/fst/crk-generator.fomabin"))


def home(request):
    return HttpResponse("")


def search(request, queryString):
    """
    Search View for /Search/:queryString:
    :queryString: needs to be exactly contained in a lemma context

    See README for Detailed API Usage

    Ordering:
        Cree:
        Exact FST Lemma
        Contains Query Lemma
        Contains Query Inflection

        English:
        Definition
    """
    # URL Decode
    queryString = unquote(queryString)
    # Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)
    print("Search: " + queryString)
    queryString = syllabics2sro(queryString)
    print("Search SRO: " + queryString)
    # To lower
    queryString = queryString.lower()

    response = dict()

    fstResult = list(fstAnalyzer.analyze(queryString))
    creeWords = list()
    englishWords = list()
    if len(fstResult) > 0:
        # Probably Cree
        # Add FST analysis to response
        response["analysis"] = fstResult[0]
        lemma = fstResult[0][0]
        print("Cree: " + lemma)
        creeWords += datafetch.fetchExactLemma(lemma)
    else:
        # Probably English
        print("English: " + queryString)
        englishWords += datafetch.fetchLemmaContainsDefinition(queryString)

    # Still searches contains since some cree like inputs can be inparsable by fst
    creeWords += datafetch.fetchContainsLemma(queryString)
    creeWords += datafetch.fetchLemmaContainsInflection(queryString)

    if len(creeWords) >= len(englishWords):
        words = creeWords
        print("Return Cree")
    else:
        words = englishWords
        print("Return English")

    # Convert to dict for json serialization
    words = list(model_to_dict(word) for word in words)

    # Remove Duplicated Lemmas
    wordIDs = set()
    uniqueWords = list()
    for word in words:
        wordID = word["id"]
        if wordID not in wordIDs:
            wordIDs.add(wordID)
            uniqueWords.append(word)

    # Populate Fields
    datafetch.fillAttributes(uniqueWords)
    datafetch.fillDefinitions(uniqueWords)
    response["words"] = uniqueWords
    return HttpResponse(json.dumps(response))


def displayWord(request, queryString):
    """
    Display Word View for /DisplayWord/:queryString:
    :queryString: needs to be exact lemma
    """
    # URL Decode
    queryString = unquote(queryString)
    # Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)
    print("DisplayWord: " + queryString)

    # Get Lemma that exactly matches the :queryString:
    # Might return multiple lemmas, get the first one. Better fix will be implmeneted on the Importer
    lemma = Lemma.objects.filter(context__exact=queryString)[0]

    # Get inflections of such lemma
    inflections = Inflection.objects.filter(fk_lemma=lemma)
    inflections = [model_to_dict(inflection) for inflection in inflections]

    # Fill Lemma Definitions
    lemma = model_to_dict(lemma)
    datafetch.fillAttributes([lemma])
    datafetch.fillDefinitions([lemma])

    # Fill Inflection Definitions
    datafetch.fillDefinitions(inflections)

    # Fill inflections with InflectionForms
    for inflection in inflections:
        inflectionForms = [model_to_dict(form) for form in InflectionForm.objects.filter(fk_inflection_id=int(inflection["id"]))]
        for form in inflectionForms:
            # Remove not used fields
            form.pop("id", None)
            form.pop("fk_inflection", None)
        inflection["inflectionForms"] = inflectionForms

    # Serialize to {"lemma": LEMMA, "inflections": {...}}
    return HttpResponse(json.dumps({"lemma": lemma, "inflections": inflections}))
