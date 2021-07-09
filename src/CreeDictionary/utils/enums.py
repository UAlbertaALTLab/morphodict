from __future__ import annotations

from enum import Enum


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
