import re
import unicodedata
from typing import Dict, Any
from urllib.parse import unquote

from cree_sro_syllabics import syllabics2sro
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from hfstol import HFSTOL

import API.datafetch as datafetch
from API.models import Inflection
from utils import hfstol_analysis_parser
from utils.shared_res_dir import shared_res_dir

# paradigm_filler = ParadigmFiller.default_filler()
descriptive_analyzer = HFSTOL.from_file(
    shared_res_dir / "fst" / "crk-descriptive-analyzer.hfstol"
)


def search(request, query_string):
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
    query_string = unquote(query_string)
    # Normalize to UTF8 NFC
    query_string = unicodedata.normalize("NFC", query_string)
    query_string = (
        query_string.replace("ā", "â")
        .replace("ē", "ê")
        .replace("ī", "î")
        .replace("ō", "ô")
    )
    query_string = syllabics2sro(query_string)
    print("Search SRO: " + query_string)
    # To lower
    query_string = query_string.lower()

    response = dict()

    fstResult = list(fstAnalyzer.analyze(query_string))
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
        print("English: " + query_string)
        englishWords += datafetch.fetch_lemma_contains_definition(query_string)

    # Still searches contains since some cree like inputs can be inparsable by fst
    creeWords += datafetch.fetchContainsLemma(query_string)
    creeWords += datafetch.fetchLemmaContainsInflection(query_string)

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


def translate_cree(request, query_string: str) -> JsonResponse:
    """
    click-in-text api

    note: returned definition is for lemma, not the queried inflected form.
    see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/wiki/Web-API for API specifications
    """

    query_string = unquote(query_string)
    query_string = unicodedata.normalize("NFC", query_string)

    response: Dict[str, Any] = {"translation": []}

    res = descriptive_analyzer.feed_in_bulk_fast([query_string])[query_string]

    for analysis in res:
        non_as_is_lemmas = Inflection.fetch_non_as_is_lemmas_by_fst_analysis(analysis)

        lemma_category = hfstol_analysis_parser.extract_lemma_and_category(analysis)
        if lemma_category is None:
            continue
        lemma, category = lemma_category
        # todo (for matt): finish this
        # try:
        #     definitions = datafetch.fetch_definitions_by_exact_lemma_and_category(lemma)

        # except (datafetch.LemmaDoesNotExist, datafetch.DefinitionDoesNotExist) as e:
        #     print(
        #         "Warning: During API query, may due to incomplete database:",
        #         file=stderr,
        #     )
        #     print(e, file=stderr)
        #     continue
        # else:
        #     response["translation"].append(
        #         {"lemma": r[0], "analysis": "".join(r[1:]), "definitions": definitions}
        #     )

    json_response = JsonResponse(response)
    json_response["Access-Control-Allow-Origin"] = "*"
    return json_response


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
