"""
constants
"""
from enum import Enum

# type alias
from typing import NewType

# types
Analysis = NewType("Analysis", str)
FSTLemma = NewType("FSTLemma", str)


class ParadigmSize(Enum):
    BASIC = "BASIC"
    FULL = "FULL"
    LINGUISTIC = "LINGUISTIC"

    @property
    def display_form(self):
        """
        the form that we show to users on paradigm table
        """
        return self.value.capitalize()


class PartOfSpeech(Enum):

    IPV = "IPV"  # preverbs
    PRON = "PRON"
    N = "N"
    IPC = "IPC"  # particles like "tanisi (hello)"
    V = "V"


# alias
POS = PartOfSpeech


class SimpleLexicalCategory(Enum):
    """
    a simplified list of lexical categories.

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

    Pron = "PRON"  # Pronoun

    @property
    def pos(self) -> POS:
        if self.is_verb():
            return POS.V
        elif self.is_noun():
            return POS.N
        elif self is SimpleLexicalCategory.IPC:
            return POS.IPC
        elif self is SimpleLexicalCategory.Pron:
            return POS.PRON
        elif self is SimpleLexicalCategory.IPV:
            return POS.IPV
        else:
            raise ValueError

    def is_verb(self):
        return self.value[0] == "V"

    def is_noun(self):
        return self.value[0] == "N"

    def to_fst_output_style(self):
        """
        >>> SimpleLexicalCategory.VAI.to_fst_output_style()
        '+V+AI'
        >>> SimpleLexicalCategory.NID.to_fst_output_style()
        '+N+I+D'
        >>> SimpleLexicalCategory.IPC.to_fst_output_style()
        '+IPC'
        """

        if self.value[0] == "N":
            return "+" + "+".join(list(self.value.upper()))
        elif self.value[0] == "V":
            return "+" + "+".join(["V", self.value[1:].upper()])
        else:
            return "+" + self.value

    def to_layout_table_name(self, paradigm_size: ParadigmSize):
        """
        >>> SimpleLexicalCategory.VAI.to_layout_table_name(ParadigmSize.BASIC)
        'vai-basic'
        >>> SimpleLexicalCategory.NID.to_layout_table_name(ParadigmSize.LINGUISTIC)
        'nid-linguistic'
        """

        return self.value.lower() + "-" + paradigm_size.value.lower()


# alias
SimpleLC = SimpleLexicalCategory
