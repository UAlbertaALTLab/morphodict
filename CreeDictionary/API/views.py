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

fstAnalyzer = FST.from_file(os.path.join(settings.BASE_DIR, "API/dictionaries/crk-analyzer.fomabin.gz"))
fstGenerator = FST.from_file(os.path.join(settings.BASE_DIR, "API/dictionaries/crk-generator.fomabin.gz"))

def home(request):
    return HttpResponse("")

"""
    Search View for /Search/:queryString:
    :queryString: needs to be exactly contained in a lemma context 

    Ordering:
        Cree:
        Exact FST Lemma
        Contains Query Lemma
        Contains Query Inflection

        English:
        Definition
"""
def search(request, queryString):
    #URL Decode
    queryString = unquote(queryString)
    #Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)
    print("Search: " + queryString)

    fstResult = list(fstAnalyzer.analyze(queryString))
    if len(fstResult) > 0:
        #Probably Cree
        lemma = fstResult[0][0]
        print("Cree: " + lemma)
        words = list()
        words += datafetch.fetchExactLemma(lemma)
        words += datafetch.fetchContainsLemma(queryString)
        words += datafetch.fetchLemmaContainsInflection(queryString)
    else:
        #Probably English
        print("English: " + queryString)
        # TODO Add English Search

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

    return HttpResponse(json.dumps({"words": uniqueWords}))

"""
    Display Word View for /DisplayWord/:queryString:
    :queryString: needs to be exact lemma
"""
def displayWord(request, queryString):
    #URL Decode
    queryString = unquote(queryString)
    #Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)
    print("DisplayWord: " + queryString)

    #Get Lemma that exactly matches the :queryString:
    #Might return multiple lemmas, get the first one. Better fix will be implmeneted on the Importer
    lemma = Lemma.objects.filter(context__exact=queryString)[0] 

    #Get inflections of such lemma
    inflections = Inflection.objects.filter(fk_lemma=lemma)
    inflections = [model_to_dict(inflection) for inflection in inflections]

    #Fill Lemma Definitions
    lemma = model_to_dict(lemma)
    datafetch.fillAttributes([lemma])
    datafetch.fillDefinitions([lemma])

    #Fill Inflection Definitions
    datafetch.fillDefinitions(inflections)

    #Fill inflections with InflectionForms
    for inflection in inflections:
        inflectionForms = [model_to_dict(form) for form in InflectionForm.objects.filter(fk_inflection_id=int(inflection["id"]))]
        for form in inflectionForms:
            #Remove not used fields
            form.pop("id", None)
            form.pop("fk_inflection", None)
        inflection["inflectionForms"] = inflectionForms
    
    #Serialize to {"lemma": LEMMA, "inflections": {...}}
    return HttpResponse(json.dumps({"lemma": lemma, "inflections":inflections}))