from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from CreeDictionary.forms import WordSearchForm


def index(request):
    context = {"word_search_form": WordSearchForm()}
    return HttpResponse(render(request, "CreeDictionary/index.html", context))
