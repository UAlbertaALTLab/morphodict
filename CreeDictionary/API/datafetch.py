from sys import stderr
from typing import List, Dict

from django.db.models import QuerySet

from API.models import *
from django.forms.models import model_to_dict
from django.db.models.functions import Length


class LemmaDoesNotExist(Exception):
    def __init__(self, query_string):
        self.msg = "No Lemma exists that matches the query string %s" % query_string

    def __str__(self):
        return self.msg


class DefinitionDoesNotExist(Exception):
    def __init__(self, query_string):
        self.msg = "No Definition exists for the lemma %s" % query_string

    def __str__(self):
        return self.msg


def fetch_exact_lemma(lemma_string: str) -> Lemma:
    """

    :raise LemmaDoesNotExist: The lemma doesn't exist in the database
    :param lemma_string:
    :return: Lemma object
    """
    results = Lemma.objects.filter(context__exact=lemma_string)
    if len(results) == 1:
        return results[0]
    elif len(results) > 1:
        print(
            "warning: fetch_exact_lemma returns two or more lemmas on query_string %s. Adopted the first result"
            % lemma_string,
            file=stderr,
        )
        return results[0]
    else:
        raise LemmaDoesNotExist(lemma_string)


def fetch_definitions_with_exact_lemma(lemma_string: str) -> List[Dict[str, str]]:
    """
    :raise LemmaDoesNotExist: The lemma doesn't exist in the database
    :param lemma_string:
    """
    lemma = fetch_exact_lemma(lemma_string)
    definitions = dict()

    definition_models = Definition.objects.filter(fk_word=lemma)
    definition_list = []
    for definition in definition_models:
        definition_list.append(
            {"definition": definition.context, "source": definition.source}
        )
    if len(definition_list) == 0:
        raise DefinitionDoesNotExist(lemma_string)
    else:
        return definition_list


def fetchContainsLemma(lemma, limit=10):
    lemmas = Lemma.objects.filter(context__icontains=lemma)[:limit]
    return lemmas


def fetchLemmaContainsInflection(inflection, limit=10):
    lemmaIDs = Inflection.objects.filter(context__icontains=inflection)[
        :limit
    ].values_list("fk_lemma_id", flat=True)
    lemmas = Lemma.objects.filter(word_ptr_id__in=lemmaIDs)
    return lemmas


def fetchLemmaContainsDefinition(definition, limit=10):
    lemmas = list()
    wordIDs = (
        Definition.objects.filter(context__icontains=definition)
        .extra(select={"length": "Length(context)"})
        .order_by("length")
        .values_list("fk_word_id", flat=True)[:10]
    )
    lemmaResult = Lemma.objects.filter(word_ptr_id__in=wordIDs)

    # Sort Lemma Based on Definition Order
    for wordID in wordIDs:
        for lemma in lemmaResult:
            if wordID == lemma.id:
                lemmas.append(lemma)
                break

    lemmaIDs = Inflection.objects.filter(word_ptr_id__in=wordIDs).values_list(
        "fk_lemma_id", flat=True
    )
    lemmas += Lemma.objects.filter(word_ptr_id__in=lemmaIDs)

    print(list(lemmas))
    return lemmas


def fillDefinitions(words):
    """
        Args:
            words (list<dict>): List of words in dictionary form
    """
    for word in words:
        definitions = Definition.objects.filter(fk_word_id=int(word["id"]))
        definitions = list(model_to_dict(definition) for definition in definitions)
        word["definitions"] = definitions


def fillAttributes(words):
    """
    Args:
        words (list<dict>): List of words in dictionary form
    """
    for word in words:
        attributes = Attribute.objects.filter(fk_lemma_id=int(word["id"]))
        attributes = list(model_to_dict(attribute) for attribute in attributes)
        word["attributes"] = attributes
