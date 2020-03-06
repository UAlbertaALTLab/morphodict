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

urlpatterns = [
    # user interface
    path("", views.index, name="cree-dictionary-index"),
    path(
        "search/<str:query_string>/",
        views.index,
        name="cree-dictionary-index-with-query",
    ),
    # word is a user-friendly alternative for the linguistic term "lemma"
    path(
        "word/<str:lemma_text>/",
        views.lemma_details,
        name="cree-dictionary-index-with-lemma",
    ),
    path("about", views.about, name="cree-dictionary-about"),
    # internal use to render boxes of search results
    path(
        "_search_results/<str:query_string>/",
        views.search_results,
        name="cree-dictionary-search-results",
    ),
    # internal use to render paradigm and detailed info for a lemma
    path(
        "_lemma_details/<int:lemma_id>/",
        views.lemma_details_internal,
        name="cree-dictionary-lemma-detail",
    ),
    # cree word translation for click-in-text #todo (for matt): this
    path(
        "_translate-cree/<str:query_string>/",
        api_views.translate_cree,
        name="cree-dictionary-word-translation-api",
    ),
    path("admin/", admin.site.urls, name="admin"),
    path(
        "change-orthography",
        views.ChangeOrthography.as_view(),
        name="cree-dictionary-change-orthography",
    ),
    # magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
    path("jsreverse/", urls_js, name="js_reverse"),
]


if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG and not settings.CI:  # pragma: no cover
    import debug_toolbar

    # necessary for debug_toolbar to work
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
