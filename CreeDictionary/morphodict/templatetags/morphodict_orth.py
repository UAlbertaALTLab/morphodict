#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from django import template
from django.utils.html import format_html

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
def orth(sro_original: str, orthography: str):
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

    conversions = {
        code: ORTHOGRAPHY.converter[code](sro_original)
        for code in ORTHOGRAPHY.available
    }
    inner_text = conversions[orthography]
    data_attributes = " ".join(f'data-orth-{code}="{{}}"' for code in conversions)
    values = tuple(conversions.values()) + (inner_text,)

    return format_html(
        # TODO: do not hardcode lang="cr" here
        '<span lang="cr" data-orth ' + data_attributes + ">{}</span>",
        *values,
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
