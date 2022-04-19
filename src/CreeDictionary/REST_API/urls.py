"""
Definition of urls for CreeDictionary.
"""

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from CreeDictionary.CreeDictionary import views
from CreeDictionary.CreeDictionary.sitemaps import sitemaps
from . import views

urlpatterns = [
    ################################# Primary URLs #################################
    path("api/", views.search_api, name="cree-dictionary-search"), #main page
    path("api/search/", views.search_api, name="cree-dictionary-search"), #word_search returns wordforms as json
    path(
        "api/word/<str:slug>/",
        views.word_details_api,
        name="cree-dictionary-index-with-lemma",
    ), #returns details related to a spesific word
]


if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG and settings.ENABLE_DJANGO_DEBUG_TOOLBAR:
    import debug_toolbar

    # necessary for debug_toolbar to work
    urlpatterns.append(path("api/__debug__/", include(debug_toolbar.urls)))
