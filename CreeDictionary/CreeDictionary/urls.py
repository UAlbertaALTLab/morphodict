"""
Definition of urls for CreeDictionary.
"""
from django_js_reverse.views import urls_js
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

import API.views as api_views
from CreeDictionary import views

# 2019/May/21 Matt Yan:

# The reason to have different rules in development/production:

# static file urls / web-page urls / API urls in this project all begin with "cree-dictionary"
# so that in production on server sapir, the cree-dictionary service can be proxy-ed by looking for
# initial "cree-dictionary" in the url.

# example url:
# http://sapir.artsrn.ualberta.ca/cree-dictionary/search/hello

# in development, though, the initial "cree-dictionary" is not needed, example:
# http://localhost:8000/search/hello
# Note: re_path here, for example "re_path("^(cree-dictionary/)?some/url")", isn't a good solution. It messes up with
# url reversion

_urlpatterns = [
    # user interface
    ("", views.index, "cree-dictionary-index"),
    ("search/<str:query_string>/", views.index, "cree-dictionary-index-with-word"),
    ("lemma/<int:lemma_id>/", views.index, "cree-dictionary-index-with-lemma"),
    # internal use to render boxes of search results
    (
        "_search_results/<str:query_string>/",
        views.search_results,
        "cree-dictionary-search-results",
    ),
    # internal use to render paradigm and detailed info for a lemma
    (
        "_lemma_details/<int:lemma_id>/",
        views.lemma_details,
        "cree-dictionary-lemma-detail",
    ),
    # cree word translation for click-in-text #todo (for matt): this
    (
        "_translate-cree/<str:query_string>/",
        api_views.translate_cree,
        "cree-dictionary-word-translation-api",
    ),
    ("admin/", admin.site.urls, "admin"),
]

urlpatterns = []
prefix = "" if settings.DEBUG else "cree-dictionary/"

for route, view, name in _urlpatterns:
    # kwarg `name` for url reversion in html/py/js code
    urlpatterns.append(path(prefix + route, view, name=name))

# magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
urlpatterns.append(url(fr"^{prefix}jsreverse/$", urls_js, name="js_reverse"))

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
