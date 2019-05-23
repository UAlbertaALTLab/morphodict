from django.contrib import admin
from django.urls import include, path, re_path

# 2019/May/21 Matt Yan:
# static file urls / web-page urls / API urls in this project all begin with "cree-dictionary"
# so that in production on server sapir, the cree-dictionary service can be proxy-ed by looking for
# initial "cree-dictionary" in the url.

# on sapir, the initial "cree-dictionary/" will be stripped away when it
# reaches this django app. That's how apache proxy works.

# example:
# http://sapir.artsrn.ualberta.ca/cree-dictionary/Search/hello
# what reaches the app on sapir is "Search/hello"

# in development, though, the initial "cree-dictionary" is not stripped away

# below "cree-dictionary/" and "/" match the url w/ or w/o
# the beginning "cree-dictionary" in development and production settings

from CreeDictionary.settings import DEBUG

if DEBUG:
    urlpatterns = [
        path("cree-dictionary", include("CreeDictionary.urls")),
        path("cree-dictionary/", include("CreeDictionary.urls")),
    ]

else:
    urlpatterns = [
        path("", include("CreeDictionary.urls")),
        path("/", include("CreeDictionary.urls")),
    ]
