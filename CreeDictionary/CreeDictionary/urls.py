"""
Definition of urls for CreeDictionary.
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django_js_reverse.views import urls_js

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


# TODO: Convert this to an idiomatic Django style when we drop support for
# Sapir and mod-wsgi.
_urlpatterns = [
    # user interface
    ("", views.index, "cree-dictionary-index"),
    ("search", views.index, "cree-dictionary-search"),
    # DEPRECATED: this route 👇 is a permanent redirect to the route above ☝️
    (
        "search/<str:query_string>/",
        views.redirect_search,
        "cree-dictionary-index-with-query",
    ),
    # word is a user-friendly alternative for the linguistic term "lemma"
    (
        "word/<str:lemma_text>/",
        views.lemma_details,
        "cree-dictionary-index-with-lemma",
    ),
    ("about", views.about, "cree-dictionary-about"),
    ("contact-us", views.contact_us, "cree-dictionary-contact-us"),
    # internal use to render boxes of search results
    (
        "_search_results/<str:query_string>/",
        views.search_results,
        "cree-dictionary-search-results",
    ),
    # internal use to render paradigm and detailed info for a lemma
    (
        "_lemma_details/<int:lemma_id>/",
        views.lemma_details_internal,
        "cree-dictionary-lemma-detail",
    ),
    # cree word translation for click-in-text #todo (for matt): this
    (
        "_translate-cree/<str:query_string>/",
        api_views.translate_cree,
        "cree-dictionary-word-translation-api",
    ),
    ("admin/", admin.site.urls, "admin"),
    (
        "change-orthography",
        views.ChangeOrthography.as_view(),
        "cree-dictionary-change-orthography",
    ),
]

# XXX: ugly hack to make this work on a local instance and on Sapir
# TODO: this should use the SCRIPT_NAME WSGI variable instead.
urlpatterns = []
prefix = "cree-dictionary/" if settings.RUNNING_ON_SAPIR else ""

for route, view, name in _urlpatterns:
    # kwarg `name` for url reversion in html/py/js code
    urlpatterns.append(path(prefix + route, view, name=name))

# magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
urlpatterns.append(url(fr"^{prefix}jsreverse/$", urls_js, name="js_reverse"))

if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

    if not settings.CI:
        import debug_toolbar

        # necessary for debug_toolbar to work
        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
