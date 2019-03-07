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

fstAnalyzer = FST.from_file(os.path.join(settings.BASE_DIR, "API/dictionaries/crk-analyzer.fomabin.gz"))
fstGenerator = FST.from_file(os.path.join(settings.BASE_DIR, "API/dictionaries/crk-generator.fomabin.gz"))

def home(request):
    return HttpResponse("")

"""
    Search View for /Search/:queryString:
    :queryString: needs to be exactly contained in a lemma context 
"""
def search(request, queryString):
    #URL Decode
    queryString = unquote(queryString)
    #Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)
    print("Search: " + queryString)

    #Get lemmas that contains :queryString: in its context
    words = Lemma.objects.filter(context__contains=queryString)
    #Convert to dict for json serialization
    words = list(model_to_dict(word) for word in words)

    fillDefinitions(words)

    return HttpResponse(json.dumps({"words": words}))

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
    fillDefinitions([lemma])

    #Fill Inflection Definitions
    fillDefinitions(inflections)

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

"""
    Args:
        words (list<dict>): List of words in dictionary form
"""
def fillDefinitions(words):
    for word in words:
        definitions = Definition.objects.filter(fk_word_id=int(word["id"]))
        definitions = list(model_to_dict(definition) for definition in definitions)
        word["definitions"] = definitions