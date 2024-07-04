#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Orthography conversion utilities.
"""

from cree_sro_syllabics import sro2syllabics

CIRCUMFLEX_TO_MACRON = str.maketrans("êîôâ", "ēīōā")
ACCENTED_Y_TO_Y = str.maketrans("ý", "y")

def to_y(latn_accented_y: str) -> str:
    """
    Translate SRO with accented y to normal y
    """
    return latn_accented_y.translate(ACCENTED_Y_TO_Y)

def to_macrons(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons.
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON)

def to_macrons_with_y(sro_circumflex: str) -> str:
    """
    Transliterate SRO to macrons with normal y
    """
    return sro_circumflex.translate(CIRCUMFLEX_TO_MACRON).translate(ACCENTED_Y_TO_Y)


def to_syllabics(sro_circumflex: str) -> str:
    """
    Transliterate SRO to syllabics.
    """
    # Get rid of - after prefixes, like nôhte-/ᓄᐦᑌ
    return sro2syllabics(sro_circumflex).rstrip("-")
