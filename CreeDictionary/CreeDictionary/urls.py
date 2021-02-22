"""
Definition of urls for CreeDictionary.
"""

import os

import API.views as api_views
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django_js_reverse.views import urls_js

from CreeDictionary import views

urlpatterns = [
    ################################# Primary URLs #################################
    path("", views.index, name="cree-dictionary-index"),
    path("search", views.index, name="cree-dictionary-search"),
    # "word" is a user-friendly alternative for the linguistic term "lemma"
    path(
        "word/<str:lemma_text>/",
        views.lemma_details,
        name="cree-dictionary-index-with-lemma",
    ),
    path("about", views.about, name="cree-dictionary-about"),
    path("contact-us", views.contact_us, name="cree-dictionary-contact-us"),
    ################################# Internal API #################################
    # internal use to render boxes of search results
    path(
        "_search_results/<str:query_string>/",
        views.search_results,
        name="cree-dictionary-search-results",
    ),
    # internal use to render paradigm and only the paradigm
    path(
        "_paradigm_details/",
        views.paradigm_internal,
        name="cree-dictionary-paradigm-detail",
    ),
    # cree word translation for click-in-text
    path(
        "click-in-text/",
        api_views.click_in_text,
        name="cree-dictionary-word-click-in-text-api",
    ),
    ############################## Other applications ##############################
    path("admin/", admin.site.urls),
    path("search-quality/", include("search_quality.urls")),
    path("", include("morphodict.urls")),
    ################################# Special URLS #################################
    # Reverse URLs in JavaScript:  https://github.com/ierror/django-js-reverse
    path("jsreverse", urls_js, name="js_reverse"),
]

if hasattr(settings, "GOOGLE_SITE_VERIFICATION"):
    urlpatterns.append(
        path(
            f"google{settings.GOOGLE_SITE_VERIFICATION}.html",
            views.google_site_verification,
        )
    )

if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG and settings.ENABLE_DJANGO_DEBUG_TOOLBAR:
    import debug_toolbar

    # necessary for debug_toolbar to work
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
