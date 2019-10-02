"""
Definition of urls for CreeDictionary.
"""
from django_js_reverse.views import urls_js
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

import API.views as api_views
from CreeDictionary import views

admin.autodiscover()

urlpatterns = [
    # user interface
    path("", views.index, name="cree-dictionary-index"),
    path(
        "search/<str:query_string>/",
        views.index,
        name="cree-dictionary-index-with-word",
    ),
    #
    # word search api which returns roughly matching
    # dictionary entries for an arbitrary string. \
    # It's also used in html templates to display to user. If this is changed,
    # static/CreeDictionary/js/app.js (which hard codes this url) needs to be updated
    # fixme: figure out url reversing in javascript.
    # A fix on stack-overflow is to render javascript with django template
    path(
        "_search/<str:query_string>/",
        api_views.search,
        name="cree-dictionary-search-api",
    ),
    # API which renders detailed definition/ inflection/ paradigms for a lemma
    # internal use
    path(
        "_lemma_details/<int:lemma_id>/",
        api_views.lemma_details,
        name="cree-dictionary-lemma-detail-api",
    ),
    # cree word translation for click-in-text #todo (for matt): this
    path(
        "_translate-cree/<str:query_string>/",
        api_views.translate_cree,
        name="cree-dictionary-word-translation-api",
    ),
    path("admin/", admin.site.urls, name="admin"),
    # magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
    url(r"^jsreverse/$", urls_js, name="js_reverse"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
