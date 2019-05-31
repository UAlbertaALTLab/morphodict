from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from CreeDictionary.forms import WordSearchForm


def index(request, query_string=None):
    """

    :param request:
    :param query_string: initial word and search results to display
    :return:
    """
    context = {"word_search_form": WordSearchForm()}
    if query_string is not None:
        context.update({"query_string": query_string})
    print("context", query_string)
    return HttpResponse(render(request, "CreeDictionary/index.html", context))


def display_word(request, query_string):
    """

    :param request:
    :param query_string: word to display paradigm for
    :return:
    """
    context = {}
    if query_string is not None:
        context.update({"query_string": query_string})

    return HttpResponse(render(request, "CreeDictionary/display-word.html", context))
