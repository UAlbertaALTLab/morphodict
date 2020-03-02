#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def orth(sro_text: str):
    """
    Filter that generates a <span> with multiple orthographical representations
    of the given text.

    e.g.,

        {{ 'wâpamêw'|multiorth }}

    Yields:

        <span lang="cr" data-orth-latn="wâpamêw" data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """

    resultant = conditional_escape(sro_text)
    return mark_safe(f'<span lang="cr" data-orth-Latn="{resultant}">{resultant}</span>')
