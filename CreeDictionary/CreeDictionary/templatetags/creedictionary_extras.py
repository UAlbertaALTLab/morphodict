#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Template tags related to the Cree Dictionary specifically.
"""


def orth():
    """
    Filter that generates a <span> with multiple orthographical representations
    of the given text.

    e.g.,

        {{ 'wâpamêw'|multiorth }}

    Yields:

        <span lang="cr" data-orth-latn="wâpamêw" data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """
