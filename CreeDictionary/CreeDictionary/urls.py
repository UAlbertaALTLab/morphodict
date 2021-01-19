"""
Definition of urls for CreeDictionary.
"""

import logging
import os

import API.views as api_views
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django_js_reverse.views import urls_js

from CreeDictionary import views

logger = logging.getLogger(__name__)

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

# 2021-01-12 Eddie Antonio Santos:
#
# I'm in the process of fixing this on Sapir.
#
# This routing code needs to know how to handle both when SCRIPT_NAME is
# specified as '/cree-dictionary' and when it's not.
#
# Then, the Gunicorn config on Sapir must be changed to supply -v
# SCRIPT_NAME='/cree-dictionary' in its startup options.
#
# The following function, as well as any comments ands hacks associated with it can be
# deleted soon!


def running_on_sapir_without_script_name():  # pragma: no cover
    """
    The WSGI SCRIPT_NAME environment variable indicates the part of the URL's path before the
    first slash handled within this application.

    Usually, SCRIPT_NAME is the empty string. On Sapir, it SHOULD be "/cree-dictionary":

                                           SCRIPT_NAME
                                        ,--------------.
                                        v              v
        https://sapir.artsrn.ualberta.ca/cree-dictionary/

    However, we have not configured it this way :/

    This function enables a hack when we're running on sapir, but the script name is not
    set.

    See: https://docs.gunicorn.org/en/stable/faq.html#how-do-i-set-script-name
    See: https://wsgi.readthedocs.io/en/latest/definitions.html#envvar-SCRIPT_NAME
    """
    wsgi_script_name = os.getenv("SCRIPT_NAME", "")

    if not settings.RUNNING_ON_SAPIR:
        return False

    if wsgi_script_name == "":
        logger.warn("Running on Sapir WITHOUT a valid script name; using hacky URLs")
        return True
    else:
        logger.info("Running on Sapir with script name: %r", wsgi_script_name)
        return False


# TODO: Convert this to an idiomatic Django style when we drop support for
# Sapir
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
        "_lemma_details/",
        views.lemma_details_internal,
        "cree-dictionary-lemma-detail",
    ),
    # cree word translation for click-in-text
    (
        "click-in-text/",
        api_views.click_in_text,
        "cree-dictionary-word-click-in-text-api",
    ),
    (
        "",
        include("morphodict.urls"),
        "cree-dictionary-change-orthography",
    ),
]

# Add style debugger, but only in DEBUG mode!
if settings.DEBUG:
    _urlpatterns.append(("styles", views.styles, "styles"))

# XXX: ugly hack to make this work on a local instance and on Sapir
urlpatterns = []
if running_on_sapir_without_script_name():  # pragma: no cover
    prefix = "cree-dictionary/"
else:
    prefix = ""

for route, view, name in _urlpatterns:
    # kwarg `name` for url reversion in html/py/js code
    urlpatterns.append(path(prefix + route, view, name=name))

# magic that allows us to reverse urls in js  https://github.com/ierror/django-js-reverse
urlpatterns.append(url(fr"^{prefix}jsreverse/$", urls_js, name="js_reverse"))

if settings.DEBUG:
    # saves the need to `manage.py collectstatic` in development
    urlpatterns += staticfiles_urlpatterns()

    if settings.ENABLE_DJANGO_DEBUG_TOOLBAR:
        import debug_toolbar

        # necessary for debug_toolbar to work
        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
