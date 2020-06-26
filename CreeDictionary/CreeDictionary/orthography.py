#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Orthography conversion utilities.
"""


CIRCUMFLEX_TO_MACRON = str.maketrans("êîôâ", "ēīōā")


def to_macrons(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons.
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON)
