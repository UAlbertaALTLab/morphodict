#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Usage:

    {% load creedictionary_orthography %}

...then:

    {% as_oaspan 'tânisi' %}

What is a an 'OASpan'?

It's a `<span>` tag that is **orthographically-aware**.

That is, when the `<span>` is rendered on the page, it can change its
orthography **dynamically**.
"""

from django import template
from django.utils.html import format_html


register = template.Library()

#################################### Tags ####################################


@register.simple_tag
def as_oaspan(sro_circumflex_text: str):
    """
    Creates an HTML tag that is capable of dynamically changing its
    orthography.
    """
    # TODO: make a custom component for this?
    return format_html('<span lang="cr" data-oaspan>{}</span>', sro_circumflex_text)
