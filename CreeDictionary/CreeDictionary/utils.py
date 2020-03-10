#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Utilities that depend on the CreeDictionary Django application.
"""

from urllib.parse import ParseResult, urlencode, urlunparse

from django.urls import reverse


def url_for_query(user_query: str) -> str:
    """
    Produces a relative URL to search for the given user query.
    """
    parts = ParseResult(
        scheme="",
        netloc="",
        params="",
        path=reverse("cree-dictionary-search"),
        query=urlencode((("q", user_query),)),
        fragment="",
    )
    return urlunparse(parts)
