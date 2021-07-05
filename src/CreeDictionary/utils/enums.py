from __future__ import annotations

from enum import Enum
from typing import Optional


class ParadigmSize(Enum):
    BASIC = "BASIC"
    FULL = "FULL"
    # TODO: "Linguistic" isn't a size...
    LINGUISTIC = "LINGUISTIC"

    @classmethod
    def from_string(cls, value: Optional[str]) -> ParadigmSize:
        if not value:
            return cls.BASIC
        return cls(value.upper())


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

    @property
    def pos(self) -> PartOfSpeech:
        if self.is_verb():
            return PartOfSpeech.V
        elif self.is_noun():
            return PartOfSpeech.N
        elif self is WordClass.IPC:
            return PartOfSpeech.IPC
        elif self is WordClass.Pron:
            return PartOfSpeech.PRON
        elif self is WordClass.IPV:
            return PartOfSpeech.IPV
        else:
            raise ValueError

    def is_verb(self):
        return self.value[0] == "V"

    def is_noun(self):
        return self.value[0] == "N"

    def has_inflections(self):
        """
        Does this word class have multiple inflections?
        Can we make a paradigm out of it?
        """
        return self.is_noun() or self.is_verb()

    def to_fst_output_style(self):
        """
        >>> WordClass.VAI.to_fst_output_style()
        '+V+AI'
        >>> WordClass.NID.to_fst_output_style()
        '+N+I+D'
        >>> WordClass.IPC.to_fst_output_style()
        '+Ipc'
        >>> WordClass.Pron.to_fst_output_style()
        '+Pron'
        """

        if self.value[0] == "N":
            return "+" + "+".join(list(self.value.upper()))
        elif self.value[0] == "V":
            return "+" + "+".join(["V", self.value[1:].upper()])
        else:
            return "+" + self.value.title()

    def without_pos(self) -> str:
        """
        >>> WordClass.VAI.without_pos()
        'AI'
        >>> WordClass.NID.without_pos()
        'ID'
        >>> WordClass.IPC.without_pos()
        'IPC'
        """
        if self.is_verb():
            assert self.value.startswith("V")
            return self.value[1:]
        if self.is_noun():
            assert self.value.startswith("N")
            return self.value[1:]
        return self.value
