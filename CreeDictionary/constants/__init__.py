"""
constants
"""
from enum import Enum
from typing import List

Table = List[List[str]]
""" a paradigm table"""


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
    IPV = "IPV"
    PRON = "PRON"
    N = "N"
    IPC = "IPC"
    V = "V"


# alias
POS = PartOfSpeech


class LexicalCategory(Enum):

    NA = "NA"
    NAD = "NAD"
    NI = "NI"
    NID = "NID"
    VAI = "VAI"
    VII = "VII"
    VTA = "VTA"
    VTI = "VTI"

    IPC = "IPC"

    Pron = "PRON"  # Pronoun

    def is_verb(self):
        return self.value[0] == "V"

    def is_noun(self):
        return self.value[0] == "N"

    def to_fst_output_style(self):
        """
        >>> LexicalCategory.VAI.to_fst_output_style()
        '+V+AI'
        >>> LexicalCategory.NID.to_fst_output_style()
        '+N+I+D'
        >>> LexicalCategory.IPC.to_fst_output_style()
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
        >>> LexicalCategory.VAI.to_layout_table_name(ParadigmSize.BASIC)
        'vai-basic'
        >>> LexicalCategory.NID.to_layout_table_name(ParadigmSize.LINGUISTIC)
        'nid-linguistic'
        """

        return self.value.lower() + "-" + paradigm_size.value.lower()


# alias
LC = LexicalCategory
