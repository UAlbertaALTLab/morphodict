#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""

from django import template
from django.utils.html import format_html

from CreeDictionary.utils import url_for_query
from morphodict.templatetags.morphodict_orth import orth_tag
from utils import ORTHOGRAPHY_NAME
from utils.vars import DEFAULT_ORTHOGRAPHY

register = template.Library()


@register.simple_tag(takes_context=True)
def cree_example(context, example):
    """
    Similart to {% orth %}, but does not convert the 'like: ' prefix.
    This should be used for the examples given in crk.altlabel.tsv.

    e.g.,

        {% cree_example 'like: wâpamêw' %}

    Yields:

        like: <span lang="cr" data-orth
              data-orth-latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """
    if not example.startswith("like: "):
        # Do nothing if it doesn't look like an example
        return example

    _like, _sp, cree = example.partition(" ")
    return format_html("like: {}", orth_tag(context, cree))


@register.simple_tag(takes_context=True)
def current_orthography_name(context):
    """
    Returns a pretty string of the currently active orthography.
    The orthography is determined by the orth= cookie in the HTTP request.
    """
    # Determine the currently requested orthography:
    request_orth = context.request.COOKIES.get("orth", DEFAULT_ORTHOGRAPHY)
    return ORTHOGRAPHY_NAME[request_orth]


@register.simple_tag(name="url_for_query")
def url_for_query_tag(user_query: str) -> str:
    """
    Same as url_for_query(query), but usable in a template:

    e.g.,

        {% url_for_query 'wâpamêw' %}

    yields:

        /search?q=w%C3%A2pam%C3%AAw
    """
    return url_for_query(user_query)
