from typing import NamedTuple

from utils.types import ConcatAnalysis


class Analysis(NamedTuple):
    """
    Analysis of a wordform.
    """

    raw_prefixes: str
    lemma: str
    raw_suffixes: str

    def concatenate(self) -> ConcatAnalysis:
        result = ""
        if self.raw_prefixes != "":
            result += self.raw_prefixes + "+"
        result += f"{self.lemma}+{self.raw_suffixes}"
        return ConcatAnalysis(result)
