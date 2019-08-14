import re
from pprint import pprint
from sys import stderr
from typing import Dict, List

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
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

from utils.paradigm import ParadigmFiller

fstAnalyzer = FST.from_file(
    os.path.join(settings.BASE_DIR, "API/fst/crk-descriptive-analyzer.fomabin")
)

paradigm_filler = ParadigmFiller.default_filler()


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
    queryString = (
        queryString.replace("ā", "â")
        .replace("ē", "ê")
        .replace("ī", "î")
        .replace("ō", "ô")
    )
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
        for item in fstResult[0]:
            if "+" not in item:
                lemma = item
        print("Cree: " + lemma)
        creeWords += [datafetch.fetch_exact_lemma(lemma)]
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
    if request.GET.get("render-html", False) == "true":
        return render(request, "API/word-entries.html", {"words": uniqueWords})
    else:
        response["words"] = uniqueWords
        return JsonResponse(response)


def translate_cree(request, queryString: str) -> JsonResponse:
    """
    note: returned definition is for lemma, not the queried inflected form.
    see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/wiki/Web-API for API specifications

    :param request:
    :param queryString:
    """

    queryString = unquote(queryString)
    queryString = unicodedata.normalize("NFC", queryString)

    response = {"translation": []}

    res = list(fstAnalyzer.analyze(queryString))

    for r in res:
        try:
            definitions = datafetch.fetch_definitions_with_exact_lemma(r[0])

        except (datafetch.LemmaDoesNotExist, datafetch.DefinitionDoesNotExist) as e:
            print(
                "Warning: During API query, may due to incomplete database:",
                file=stderr,
            )
            print(e, file=stderr)
            continue
        else:
            response["translation"].append(
                {"lemma": r[0], "analysis": "".join(r[1:]), "definitions": definitions}
            )
    response = JsonResponse(response)
    response["Access-Control-Allow-Origin"] = "*"
    return response


def displayWord(request, queryString):
    """
    Display Word View for /DisplayWord/:queryString:
    :queryString: needs to be exact lemma
    """
    # URL Decode
    queryString = unquote(queryString)
    # Normalize to UTF8 NFC
    queryString = unicodedata.normalize("NFC", queryString)

    print(queryString)

    if request.GET.get("render-html", False) == "true":

        lemma = model_to_dict(Lemma.objects.filter(context__exact=queryString)[0])
        lemma_name = lemma["context"]

        tags = ""
        datafetch.fillAttributes([lemma])
        datafetch.fillDefinitions([lemma])
        lemma_definitions = []
        for definition in lemma["definitions"]:
            lemma_definitions.append(
                {"context": definition["context"], "source": definition["source"]}
            )

        lemma_tags = []
        for tag in lemma["attributes"]:

            # 06/07/2019 fst analyzer gives 'tânisi+Err/Orth+Ipc' that breaks this part
            if tag["name"] != "Err/Orth":
                tags += tag["name"]
                lemma_tags.append(tag["name"])
        # print("dang")
        # print(tags)
        # pprint(lemma)
        print(lemma)
        if lemma_tags:
            groups = re.match(".*(NAD?|NID?|VAI|VII|VT[AI]|Ipc).*", tags).groups()
            if groups:
                lemma_layout_class = groups[0]
                table = paradigm_filler.fill_paradigm(lemma_name)
            else:
                table = []
            # print(lemma_tags)

        else:
            lemma_tags = lemma["type"]
            table = []

        return render(
            request,
            "API/paradigm.html",
            {
                "lemma_name": lemma_name,
                "lemma_definitions": lemma_definitions,
                "table": table,
                "lemma_tags": lemma_tags,
            },
        )
    else:
        # Serialize to {"lemma": LEMMA, "inflections": {...}}
        print("DisplayWord: " + queryString)

        # Get Lemma that exactly matches the :queryString:
        # Might return multiple lemmas, get the first one. Better fix will be implmeneted on the Importer
        lemma = Lemma.objects.filter(context__exact=queryString)[0]

        # Get inflections of such lemma
        inflections = Inflection.objects.filter(fk_lemma=lemma)
        inflections = [model_to_dict(inflection) for inflection in inflections]

        print(inflections)

        # Fill Lemma Definitions
        lemma = model_to_dict(lemma)
        datafetch.fillAttributes([lemma])
        datafetch.fillDefinitions([lemma])

        # Fill Inflection Definitions
        datafetch.fillDefinitions(inflections)

        # Fill inflections with InflectionForms
        for inflection in inflections:
            inflectionForms = [
                model_to_dict(form)
                for form in InflectionForm.objects.filter(
                    fk_inflection_id=int(inflection["id"])
                )
            ]
            for form in inflectionForms:
                # Remove not used fields
                form.pop("id", None)
                form.pop("fk_inflection", None)
            inflection["inflectionForms"] = inflectionForms

        print(inflections)

        return JsonResponse({"lemma": lemma, "inflections": inflections})


# def analyze_tags(word: str):
#     """
#
#     :param word: cree word, non exact forms allowed
#     """
#     res = list(fstAnalyzer.analyze(word))
#     if res:
#         for r in fstAnalyzer.analyze(word):
#             print("".join(r))
#     else:
#         print("Analyzer returned no result")
