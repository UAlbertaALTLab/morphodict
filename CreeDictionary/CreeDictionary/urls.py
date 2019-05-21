"""
Definition of urls for CreeDictionary.
"""

from django.conf.urls import include, url
from django.urls import path, re_path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from . import views

admin.autodiscover()


# 2019/May/21 Matt Yan:
# to add/modify any url, say 'some/url', you should add/modify two versions of it
# 1. path("some/url", views.some_view)
# 2. path("cree-dictionary/some/url", views.some_view, name='some_name')

# The latter is named so that it can be "reversed" by django. See how it works at
# https://docs.djangoproject.com/en/2.2/topics/http/urls/#reverse-resolution-of-urls
# you should not hard code urls in html or code but use {url} tag/reverse() all the time.

# The reason to do this:
# as commented in cree-intelligent-dictionary/CreeDictionary/urls.py The production server strips away cree-dictionary/
# We have 'some/url' so that we can cope with the stripped url.
# The second named url is purely for the proxy setup on server sapir
# To embed urls in templates/code, we should use  {% url 'some_name' %} /reverse('some_name'),
# which gives "cree-dictionary/some/url" so that the url is preceded by "cree-dictionary/". This makes sure
# server sapir can recognize the url and proxy the rest of the url to the app.

# Note: use re_path here, for example "re_path("^(cree-dictionary/)?some/url")", isn't a solution. It messes up with
# url reverse and may not generate the preceding 'cree-dictionary/'

# 2 alternative solutions:
# 1. Have this run on a isolated environment in production. Instead of sapir where it's crowded with services so we
# have to use a proxy to redirect cree-dictionary/ urls.
# 2. Set up a url rewrite rule in .conf file on server sapir. We can make a rule where
# every "cree-dictionary/" is rewritten to "cree-dictionary/cree-dictionary/" so that only the first is stripped away.

urlpatterns = [
    path("", views.index),
    path("cree-dictionary", views.index, name="cree-dictionary-index"),
    # path("", views.index, name="index"),
    # # path("React", include("React.urls")),
    # # url(r'^React',include('React.urls')),
    # # Examples:
    # # url(r'^$', CreeDictionary.views.home, name='home'),
    # # url(r'^CreeDictionary/', include('CreeDictionary.CreeDictionary.urls')),
    # # Uncomment the admin/doc line below to enable admin documentation:
    # url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    # # Uncomment the next line to enable the admin:
    # # url(r'^admin/', include(admin.site.urls)),
    # path("cree-dictionary/Search/<str:queryString>", views.search, name="Search"),
    # path("Search/", views.search, name="Search"),
    # path("Search/<str:queryString>", views.search, name="Search"),
    # path(
    #     "cree-dictionary/DisplayWord/<str:queryString>",
    #     views.displayWord,
    #     name="DisplayWord",
    # ),
    # path("DisplayWord/<str:queryString>", views.displayWord, name="DisplayWord"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
