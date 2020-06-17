from enum import Enum


class Language(Enum):
    ENGLISH = "ENGLISH"
    CREE = "CREE"


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

    def to_fst_output_style(self):
        """
        >>> WordClass.VAI.to_fst_output_style()
        '+V+AI'
        >>> WordClass.NID.to_fst_output_style()
        '+N+I+D'
        >>> WordClass.IPC.to_fst_output_style()
        '+IPC'
        """

        if self.value[0] == "N":
            return "+" + "+".join(list(self.value.upper()))
        elif self.value[0] == "V":
            return "+" + "+".join(["V", self.value[1:].upper()])
        else:
            return "+" + self.value

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

    def to_layout_table_name(self, paradigm_size: ParadigmSize):
        """
        >>> WordClass.VAI.to_layout_table_name(ParadigmSize.BASIC)
        'vai-basic'
        >>> WordClass.NID.to_layout_table_name(ParadigmSize.LINGUISTIC)
        'nid-linguistic'
        """

        return self.value.lower() + "-" + paradigm_size.value.lower()
