#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""

from cree_sro_syllabics import sro2syllabics
from django import template
from django.utils.html import format_html

CIRCUMFLEX_TO_MACRON = str.maketrans("êîôâ", "ēīōā")

register = template.Library()


@register.filter
def orth(sro_original: str):
    """
    Filter that generates a <span> with multiple orthographical representations
    of the given text.

    e.g.,

        {{ 'wâpamêw'|orth }}

    Yields:

        <span lang="cr" data-orth
              data-orth-latn="wâpamêw"
              data-orth-latn="wāpamēw"
              data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """

    sro_circumflex = sro_original
    sro_macrons = to_macrons(sro_original)
    syllabics = sro2syllabics(sro_original)

    return format_html(
        '<span lang="cr" data-orth '
        'data-orth-Latn="{}" '
        'data-orth-Latn-x-macron="{}" '
        'data-orth-Cans="{}">{}</span>',
        sro_circumflex,
        sro_macrons,
        syllabics,
        sro_circumflex,
    )


def to_macrons(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons.
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON)
