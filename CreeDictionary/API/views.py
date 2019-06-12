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

from API.layout_filler import fill

fstAnalyzer = FST.from_file(
    os.path.join(settings.BASE_DIR, "API/fst/crk-descriptive-analyzer.fomabin")
)

paradigm_filler = fill.ParadigmFiller.default_filler()


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
    result looks like:
    [{'lemma':'niskak','analysis':'niska+N+A+Pl', 'definitions':{'definition':'goose', 'source':'cw'}},
    {...},]

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

    return JsonResponse(response)


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
                table = paradigm_filler.fill_paradigm(
                    lemma_layout_class.lower() + "-full", lemma_name
                )
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


c = {
    "words": [
        {
            "id": 201607,
            "context": "t\u00e2nisi",
            "type": "Ipc",
            "language": "crk",
            "word_ptr": 201607,
            "attributes": [{"id": 5479, "name": "Ipc", "fk_lemma": 201607}],
            "definitions": [
                {
                    "id": 1933,
                    "context": "How are you?",
                    "source": "MD",
                    "fk_word": 201607,
                },
                {
                    "id": 1936,
                    "context": "how, in what way",
                    "source": "CW",
                    "fk_word": 201607,
                },
                {
                    "id": 1939,
                    "context": "hello, how are you",
                    "source": "CW",
                    "fk_word": 201607,
                },
            ],
        }
    ]
}


{
    "words": [
        {
            "id": 694110,
            "context": "cahkipehikanisak",
            "type": "N",
            "language": "crk",
            "word_ptr": 694110,
            "attributes": [],
            "definitions": [
                {
                    "id": 6282,
                    "context": "All the syllabgic symbol endings (finals). [Plural]",
                    "source": "MD",
                    "fk_word": 694110,
                }
            ],
        },
        {
            "id": 1473966,
            "context": "kaspipakwesikanisak",
            "type": "N",
            "language": "crk",
            "word_ptr": 1473966,
            "attributes": [],
            "definitions": [
                {
                    "id": 13794,
                    "context": "Crackers for soup.",
                    "source": "MD",
                    "fk_word": 1473966,
                }
            ],
        },
        {
            "id": 96531,
            "context": "iskot\u00eawit\u00e2p\u00e2n",
            "type": "N",
            "language": "crk",
            "word_ptr": 96531,
            "attributes": [
                {"id": 3711, "name": "N", "fk_lemma": 96531},
                {"id": 3717, "name": "A", "fk_lemma": 96531},
                {"id": 3723, "name": "Sg", "fk_lemma": 96531},
            ],
            "definitions": [
                {"id": 1107, "context": "train", "source": "CW", "fk_word": 96531}
            ],
        },
        {
            "id": 118065,
            "context": "iskw\u00easisihk\u00e2n",
            "type": "N",
            "language": "crk",
            "word_ptr": 118065,
            "attributes": [
                {"id": 4509, "name": "N", "fk_lemma": 118065},
                {"id": 4515, "name": "A", "fk_lemma": 118065},
                {"id": 4521, "name": "Sg", "fk_lemma": 118065},
            ],
            "definitions": [
                {"id": 1281, "context": "barley", "source": "CW", "fk_word": 118065},
                {"id": 1287, "context": "girl doll", "source": "CW", "fk_word": 118065},
            ],
        },
        {
            "id": 120705,
            "context": "iskw\u00eaw-atosk\u00eay\u00e2kan",
            "type": "N",
            "language": "crk",
            "word_ptr": 120705,
            "attributes": [
                {"id": 4653, "name": "N", "fk_lemma": 120705},
                {"id": 4659, "name": "A", "fk_lemma": 120705},
                {"id": 4665, "name": "Sg", "fk_lemma": 120705},
            ],
            "definitions": [
                {
                    "id": 1323,
                    "context": "maid, female servant; woman's servant",
                    "source": "CW",
                    "fk_word": 120705,
                }
            ],
        },
        {
            "id": 314232,
            "context": "asikan",
            "type": "N",
            "language": "crk",
            "word_ptr": 314232,
            "attributes": [
                {"id": 7428, "name": "N", "fk_lemma": 314232},
                {"id": 7434, "name": "A", "fk_lemma": 314232},
                {"id": 7440, "name": "Sg", "fk_lemma": 314232},
            ],
            "definitions": [
                {"id": 2466, "context": "Sock.", "source": "MD", "fk_word": 314232},
                {
                    "id": 2472,
                    "context": "sock, stocking",
                    "source": "CW",
                    "fk_word": 314232,
                },
            ],
        },
        {
            "id": 328908,
            "context": "askihkohk\u00e2n",
            "type": "N",
            "language": "crk",
            "word_ptr": 328908,
            "attributes": [
                {"id": 7890, "name": "N", "fk_lemma": 328908},
                {"id": 7896, "name": "A", "fk_lemma": 328908},
                {"id": 7902, "name": "Sg", "fk_lemma": 328908},
            ],
            "definitions": [
                {
                    "id": 17090,
                    "context": "train engine, steam engine; engine, motor",
                    "source": "CW",
                    "fk_word": 328908,
                }
            ],
        },
        {
            "id": 329286,
            "context": "askihkohk\u00e2nis",
            "type": "N",
            "language": "crk",
            "word_ptr": 329286,
            "attributes": [
                {"id": 7908, "name": "N", "fk_lemma": 329286},
                {"id": 7914, "name": "A", "fk_lemma": 329286},
                {"id": 7920, "name": "Sg", "fk_lemma": 329286},
            ],
            "definitions": [
                {
                    "id": 17096,
                    "context": "tractor; motor",
                    "source": "CW",
                    "fk_word": 329286,
                }
            ],
        },
        {
            "id": 471182,
            "context": "t\u00e2sahikan",
            "type": "N",
            "language": "crk",
            "word_ptr": 471182,
            "attributes": [
                {"id": 12692, "name": "N", "fk_lemma": 471182},
                {"id": 12698, "name": "A", "fk_lemma": 471182},
                {"id": 12704, "name": "Sg", "fk_lemma": 471182},
            ],
            "definitions": [
                {
                    "id": 4712,
                    "context": "A file or a grindstone.",
                    "source": "MD",
                    "fk_word": 471182,
                },
                {
                    "id": 4718,
                    "context": "whetstone, file, grind stone",
                    "source": "CW",
                    "fk_word": 471182,
                },
            ],
        },
        {
            "id": 607281,
            "context": "kaskit\u00eawistikw\u00e2n",
            "type": "N",
            "language": "crk",
            "word_ptr": 607281,
            "attributes": [
                {"id": 20121, "name": "N", "fk_lemma": 607281},
                {"id": 20127, "name": "A", "fk_lemma": 607281},
                {"id": 20133, "name": "Sg", "fk_lemma": 607281},
            ],
            "definitions": [
                {
                    "id": 4689,
                    "context": "brunette, one with dark hair",
                    "source": "CW",
                    "fk_word": 607281,
                }
            ],
        },
        {
            "id": 1009026,
            "context": "iskw\u00eac\u00e2kan",
            "type": "N",
            "language": "crk",
            "word_ptr": 1009026,
            "attributes": [
                {"id": 27126, "name": "N", "fk_lemma": 1009026},
                {"id": 27132, "name": "A", "fk_lemma": 1009026},
                {"id": 27138, "name": "Sg", "fk_lemma": 1009026},
            ],
            "definitions": [
                {
                    "id": 9540,
                    "context": "A girl child ina family.",
                    "source": "MD",
                    "fk_word": 1009026,
                },
                {
                    "id": 9546,
                    "context": "last child, youngest child",
                    "source": "CW",
                    "fk_word": 1009026,
                },
            ],
        },
    ]
}
