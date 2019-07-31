from enum import Enum
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]  # python 3.5 compatible


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
