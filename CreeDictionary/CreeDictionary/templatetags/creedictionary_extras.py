#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""

from cree_sro_syllabics import sro2syllabics
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

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

    sro_circumflex = conditional_escape(sro_original)
    sro_macrons = conditional_escape(to_macrons(sro_original))
    syllabics = conditional_escape(sro2syllabics(sro_original))

    return mark_safe(
        '<span lang="cr" data-orth '
        f'data-orth-Latn="{sro_circumflex}" '
        f'data-orth-Latn-x-macron="{sro_macrons}"'
        f'data-orth-Cans="{syllabics}">{sro_circumflex}</span>'
    )


def to_macrons(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons.
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON)
