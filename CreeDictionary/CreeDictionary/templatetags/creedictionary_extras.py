#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""

from constants import DEFAULT_ORTHOGRAPHY, ORTHOGRAPHY_NAME
from cree_sro_syllabics import sro2syllabics
from CreeDictionary.utils import url_for_query
from django import template
from django.utils.html import format_html

CIRCUMFLEX_TO_MACRON = str.maketrans("êîôâ", "ēīōā")

register = template.Library()


@register.simple_tag(name="orth", takes_context=True)
def orth_tag(context, sro_original):
    """
    Tag that generates a <span> with multiple orthographical representations
    of the given text, in SRO. The inner text is determined by the
    orth= cookie in the HTTP request.

    e.g.,

        {% orth 'wâpamew' %}

    Yields:

        <span lang="cr" data-orth
              data-orth-latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """
    # Determine the currently requested orthography:
    request_orth = context.request.COOKIES.get("orth", DEFAULT_ORTHOGRAPHY)
    return orth(sro_original, orthography=request_orth)


@register.simple_tag(takes_context=True)
def current_orthography_name(context):
    """
    Returns a pretty string of the currently active orthography.
    The orthography is determined by the orth= cookie in the HTTP request.
    """
    # Determine the currently requested orthography:
    request_orth = context.request.COOKIES.get("orth", DEFAULT_ORTHOGRAPHY)
    return ORTHOGRAPHY_NAME[request_orth]


@register.filter
def orth(sro_original: str, orthography):
    """
    Filter that generates a <span> with multiple orthographical representations
    of the given text.

    e.g.,

        {{ 'wâpamêw'|orth }}

    Yields:

        <span lang="cr" data-orth
              data-orth-latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """

    sro_circumflex = sro_original
    sro_macrons = to_macrons(sro_original)
    # Strip "-" from either end of the syllabics.
    syllabics = sro2syllabics(sro_original).strip("-")

    assert orthography in ORTHOGRAPHY_NAME
    if orthography == "Latn":
        inner_text = sro_circumflex
    elif orthography == "Latn-x-macron":
        inner_text = sro_macrons
    elif orthography == "Cans":
        inner_text = syllabics

    return format_html(
        '<span lang="cr" data-orth '
        'data-orth-Latn="{}" '
        'data-orth-Latn-x-macron="{}" '
        'data-orth-Cans="{}">{}</span>',
        sro_circumflex,
        sro_macrons,
        syllabics,
        inner_text,
    )


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


def to_macrons(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons.
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON)
