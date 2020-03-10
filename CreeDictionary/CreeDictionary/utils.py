#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Utilities that depend for the CreeDictionary Django application.
"""

from django.urls import reverse


def url_for_query(user_query: str) -> str:
    path = reverse("cree-dictionary-search")
    return f"{path}?q={user_query}"
