"""
Definition of urls for morphodict.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django_js_reverse.views import urls_js

from morphodict.frontend import views
from morphodict.frontend.sitemaps import sitemaps


# TODO: use URL namespaces:
# e.g., dictionary:index instead of dictionary-index
# See: https://docs.djangoproject.com/en/2.2/topics/http/urls/#url-namespaces

urlpatterns = [
    ################################# Primary URLs #################################
    path("", views.index, name="dictionary-index"),
    path("search", views.index, name="dictionary-search"),
    # "word" is a user-friendly alternative for the linguistic term "lemma"
    path(
        "word/<str:slug>/",
        views.entry_details,
        name="dictionary-index-with-lemma",
    ),
    path("about", views.about, name="dictionary-about"),
    path("contact-us", views.contact_us, name="dictionary-contact-us"),
    path("query-help", views.query_help, name="dictionary-query-help"),
    path("legend", views.legend, name="dictionary-legend"),
    path("settings", views.settings_page, name="dictionary-settings"),
    path("admin/fst-tool", views.fst_tool, name="dictionary-fst-tool"),
    ################################# Internal API #################################
    # internal use to render boxes of search results
    path(
        "_search_results/<str:query_string>/",
        views.search_results,
        name="dictionary-search-results",
    ),
    # See morphodict.preference.urls for all available views
    # Hint: You will probably use preference:change the most!
    path("_preference/", include("morphodict.preference.urls", namespace="preference")),
    ############################## Other applications ##############################
    path("admin/", admin.site.urls),
    path("search-quality/", include("morphodict.search_quality.urls")),
    path("", include("morphodict.orthography.urls")),
    path("", include("morphodict.api.urls")),
    path("", include("morphodict.paradigm.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    ################################# Special URLS #################################
    # Reverse URLs in JavaScript:  https://github.com/ierror/django-js-reverse
    path("jsreverse", urls_js, name="js_reverse"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="user_login"),
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
