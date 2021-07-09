from __future__ import annotations

from enum import Enum


class PartOfSpeech(Enum):
    """
    This is a deprecated terminology, it exists for the source xml file uses the abbreviation "pos"

    It shouldn't be used anywhere else than the code that deals with the source files and its derived data.
    """

    # TODO: tell me if the preverb is declinable or not.
    # i.e., whether it can have a paradigm.
    IPV = "IPV"  # preverbs
    PRON = "PRON"
    N = "N"
    IPC = "IPC"  # particles like "tanisi (hello)"
    V = "V"


class WordClass(Enum):
    """
    a simplified version of inflectional categories.

    i.e. without the nuances of dash number like NA-1 VTA-3
    """

    NA = "NA"
    NAD = "NAD"
    NI = "NI"
    NID = "NID"
    VAI = "VAI"
    VII = "VII"
    VTA = "VTA"
    VTI = "VTI"

    IPC = "IPC"  # particles like "tanisi (hello)"
    IPV = "IPV"  # preverbs

    # TODO: should these both be "Pron"? That *is* what the FST generates!
    Pron = "PRON"  # Pronoun
