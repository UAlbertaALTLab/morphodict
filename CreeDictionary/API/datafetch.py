from API.models import *
from django.forms.models import model_to_dict

# Exact Lemma
def fetchExactLemma(lemma):
    lemmas = Lemma.objects.filter(context__exact=lemma)
    return lemmas

def fetchContainsLemma(lemma):
    lemmas = Lemma.objects.filter(context__contains=lemma)
    return lemmas

def fetchLemmaContainsInflection(inflection):
    lemmaIDs = Inflection.objects.filter(context__contains=inflection).values_list("fk_lemma_id", flat=True)
    lemmas = Lemma.objects.filter(word_ptr_id__in=lemmaIDs)
    return lemmas

"""
    Args:
        words (list<dict>): List of words in dictionary form
"""
def fillDefinitions(words):
    for word in words:
        definitions = Definition.objects.filter(fk_word_id=int(word["id"]))
        definitions = list(model_to_dict(definition) for definition in definitions)
        word["definitions"] = definitions

"""
    Args:
        words (list<dict>): List of words in dictionary form
"""
def fillAttributes(words):
    for word in words:
        attributes = Attribute.objects.filter(fk_lemma_id=int(word["id"]))
        attributes = list(model_to_dict(attribute) for attribute in attributes)
        word["attributes"] = attributes