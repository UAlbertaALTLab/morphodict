from enum import Enum
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]  # python 3.5 compatible


class ParadigmSize(Enum):
    BASIC = "BASIC"
    FULL = "FULL"
    EXTENDED = "EXTENDED"


class InflectionCategory(Enum):

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
        >>> InflectionCategory.VAI.to_fst_output_style()
        '+V+AI'
        >>> InflectionCategory.NID.to_fst_output_style()
        '+N+I+D'
        >>> InflectionCategory.IPC.to_fst_output_style()
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
        >>> InflectionCategory.VAI.to_layout_table_name(ParadigmSize.BASIC)
        'vai-basic'
        >>> InflectionCategory.NID.to_layout_table_name(ParadigmSize.EXTENDED)
        'nid-extended'
        """

        return self.value.lower() + "-" + paradigm_size.value.lower()
