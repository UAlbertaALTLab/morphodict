#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Usage:

    {% load creedictionary_orthography %}

...then:

    {% as_oaspan 'tânisi' %}

...or:

    {{ 'tâpwê' | in_current_orthography }}

What is a an 'OASpan'?

It's a `<span>` tag that is **orthographically-aware**.

That is, when the `<span>` is rendered on the page, it can change its
orthography **dynamically**.
"""

import unicodedata

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html
from cree_sro_syllabics import sro2syllabics, syllabics2sro


register = template.Library()

# The following functions convert SRO-circumflex to some other orthography.
ORTHOGRAPHY_CONVERTER = {
    "Cans": sro2syllabics,
    # Nothing is converted:
    "Latn": lambda text: text,
    # NOTE: The converter for Latn-x-macron is added later in this file.
}

CIRCUMFLEX_TO_MACRON = str.maketrans("êîôâ", "ēīōā")


################################## Filters ##################################


@register.filter(is_safe=True)
@stringfilter
def in_current_orthography(var: str) -> str:
    """
    A filter that converts its text into the currently set orthography.

    For example, if my host writing system is 'Cans' (syllabics), then using
    this tag as follows:

        <h1>{{ 'tânisi'|in_current_orthography }}</h1>

    Will yield::

        <h1>ᑖᓂᓯ</h1>

    """
    # TODO: get current orthography setting: from the request?
    orthography = "Cans"
    return _convert(var, orthography)


#################################### Tags ####################################


@register.simple_tag
def as_oaspan(sro_circumflex_text: str):
    """
    Creates an HTML tag that is capable of dynamically changing its
    orthography.
    """
    # TODO: make a custom component for this?
    return format_html('<span lang="cr" data-oaspan>{}</span>', sro_circumflex_text)


################################## Helpers ##################################


def _circumflex_to_macrons(text):
    """
    >>> _circumflex_to_macrons('êwêpâpîhkêwêpinamôhk')
    'ēwēpāpīhkēwēpinamōhk'
    """
    str.translate
    return unicodedata.normalize("NFC", text).translate(CIRCUMFLEX_TO_MACRON)


ORTHOGRAPHY_CONVERTER["Latn-x-macron"] = _circumflex_to_macrons


def _convert(text, orthography):
    """
    Actually does orthography conversion.
    >>> _convert('tânisi', 'Cans')
    'ᑖᓂᓯ'
    >>> _convert('tânisi', 'Latn')
    'tânisi'
    >>> _convert('tânisi', 'Latn-x-macron')
    'tānisi'
    """

    if orthography not in ORTHOGRAPHY_CONVERTER:
        orthographies = ", ".join(repr(key) for key in ORTHOGRAPHY_CONVERTER)
        raise ValueError(
            f"invalid orthography {orthography!r} " "choose from {orthographies}"
        )
    return ORTHOGRAPHY_CONVERTER[orthography](text)
