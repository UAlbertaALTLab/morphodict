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

def search(request, queryString):
    queryString = unquote(queryString)
    queryString = unicodedata.normalize("NFC", queryString)
    print("Search: " + queryString)
    words = Lemma.objects.filter(context__contains=queryString)
    words = list(model_to_dict(word) for word in words)
    return HttpResponse(json.dumps({"words": words}))

def displayWord(request, queryString):
    queryString = unquote(queryString)
    queryString = unicodedata.normalize("NFC", queryString)
    print("DisplayWord: " + queryString)
    lemma = Lemma.objects.filter(context__exact=queryString)[0]
    inflections = Inflection.objects.filter(fk_lemma=lemma)
    inflections = [model_to_dict(inflection) for inflection in inflections]
    for inflection in inflections:
        inflectionForms = [model_to_dict(form) for form in InflectionForm.objects.filter(fk_inflection_id=int(inflection["id"]))]
        for form in inflectionForms:
            form.pop("id", None)
            form.pop("fk_inflection", None)
        inflection["inflectionForms"] = inflectionForms
    return HttpResponse(json.dumps({"lemma": model_to_dict(lemma), "inflections":inflections}))