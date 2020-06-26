#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# TODO: remove this import:
from cree_sro_syllabics import sro2syllabics
from django import template
from django.utils.html import format_html

from CreeDictionary.orthography import to_macrons

from ..orthography import ORTHOGRAPHY

register = template.Library()


@register.simple_tag(name="orth", takes_context=True)
def orth_tag(context, sro_original: str) -> str:
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
    request_orth = context.request.COOKIES.get("orth", ORTHOGRAPHY.default)
    return orth(sro_original, orthography=request_orth)


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

    assert orthography in ORTHOGRAPHY.available
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


@register.simple_tag(takes_context=True)
def current_orthography_name(context):
    """
    Returns a pretty string of the currently active orthography.
    The orthography is determined by the orth= cookie in the HTTP request.
    """
    # Determine the currently requested orthography:
    request_orth = context.request.COOKIES.get("orth", ORTHOGRAPHY.default)
    return ORTHOGRAPHY.name_of(request_orth)
