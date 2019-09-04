"""
Definition of urls for CreeDictionary.
"""
import os
from distutils.util import strtobool

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import path

import API.views as api_views
from CreeDictionary import views

admin.autodiscover()

# 2019/May/21 Matt Yan:

# The reason to have different rules in development/production:

# static file urls / web-page urls / API urls in this project all begin with "cree-dictionary"
# so that in production on server sapir, the cree-dictionary service can be proxy-ed by looking for
# initial "cree-dictionary" in the url.
# on sapir, the initial "cree-dictionary/" will be stripped away when it
# reaches this django app. That's how apache proxy works.
# example:
# http://sapir.artsrn.ualberta.ca/cree-dictionary/Search/hello
# what reaches the app on sapir is "Search/hello"
# in development, though, the initial "cree-dictionary" is not stripped away
# Note: re_path here, for example "re_path("^(cree-dictionary/)?some/url")", isn't a good solution. It messes up with
# url reversion

_urlpatterns = [
    # user interface
    ("", views.index, "cree-dictionary-index"),
    ("search/<str:query_string>/", views.index, "cree-dictionary-index-with-word"),
    (
        "displayWord/<str:queryString>/",
        views.display_word,
        "cree-dictionary-word-detail",
    ),
    # word search api which returns roughly matching
    # dictionary entries for an arbitrary string. \
    # It's also used in html templates to display to user. If this is changed,
    # static/CreeDictionary/js/app.js (which hard codes this url) needs to be updated
    # fixme: figure out url reversing in javascript.
    # A fix on stack-overflow is to render javascript with django template
    ("_search/<str:queryString>/", api_views.search, "cree-dictionary-search-api"),
    # API which returns detailed definition/ inflection/ paradigms of a word
    # the query string has to be an existing cree word from the dictionary.
    # It's also used in html templates to display to user. If this is changed, app.js needs to be updated
    (
        "_displayWord/<str:queryString>/",
        api_views.displayWord,
        "cree-dictionary-word-detail-api",
    ),
    # cree word translation for click-in-text
    (
        "_translate-cree/<str:queryString>/",
        api_views.translate_cree,
        "cree-dictionary-word-translation-api",
    ),
    ("admin/", admin.site.urls, "admin"),
]

urlpatterns = []
prefix = ""

DEBUG = settings.DEBUG

for route, view, name in _urlpatterns:

    # kwarg `name` for url reversion in html/py code
    urlpatterns.append(path("cree-dictionary/" + route, view, name=name))
    if not DEBUG:
        urlpatterns.append(path(route, view))

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
