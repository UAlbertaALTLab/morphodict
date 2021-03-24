from typing import NamedTuple, Union, Set, NewType, Iterable, Tuple

from typing_extensions import Protocol

from API.models import Wordform
from API.schema import SerializedLinguisticTag
from utils.fst_analysis_parser import LABELS
from utils.types import ConcatAnalysis, FSTTag

# it's a str when the preverb does not exist in the database
Preverb = Union[Wordform, str]
Lemma = NewType("Lemma", Wordform)
MatchedEnglish = NewType("MatchedEnglish", str)
InternalForm = NewType("InternalForm", str)


class CreeResult(NamedTuple):
    """
    - analysis: a string, fst analysis of normatized cree

    - normatized_cree: a wordform, the Cree inflection that matches the analysis
        Can be a string that's not saved in the database since our database do not store all the
        weird inflections

    - lemma: a Wordform object, the lemma of the matched inflection
    """

    analysis: ConcatAnalysis
    normatized_cree: Union[Wordform, str]
    lemma: Lemma

    @property
    def normatized_cree_text(self) -> str:
        if isinstance(self.normatized_cree, Wordform):
            return self.normatized_cree.text
        else:  # is str
            return self.normatized_cree

    @classmethod
    def from_wordform(cls, wordform: Wordform) -> "CreeResult":
        return cls(wordform.analysis, wordform, wordform.lemma)


class EnglishResult(NamedTuple):
    """
    - matched_english: a string, the English that matches user query, currently it will just be the same as user query.
        (unicode normalized, lowercased)

    - normatized_cree: a string, the Cree inflection that matches the English

    - lemma: a Wordform object, the lemma of the matched inflection
    """

    matched_english: MatchedEnglish
    matched_cree: Wordform
    lemma: Lemma


class CreeAndEnglish(NamedTuple):
    """
    Duct tapes together two kinds of search results:

     - cree results -- an ordered set of CreeResults, should be sorted by the modified levenshtein distance between the
        analysis and the matched normatized form
     - english results -- an ordered set of EnglishResults, sorting mechanism is to be determined
    """

    # MatchedCree are inflections
    cree_results: Set[CreeResult]
    english_results: Set[EnglishResult]


class LinguisticTag(Protocol):
    """
    A linguistic feature/tag pair.
    """

    @property
    def value(self) -> FSTTag:
        ...

    # TODO: linguistic feature

    @property
    def in_plain_english(self) -> str:
        ...

    def serialize(self) -> SerializedLinguisticTag:
        return SerializedLinguisticTag(
            value=self.value,
            in_plain_english=self.in_plain_english,
        )


class SimpleLinguisticTag(LinguisticTag):
    """
    A linguistic feature/tag pair.
    """

    def __init__(self, value: FSTTag):
        self._value = value

    @property
    def value(self) -> FSTTag:
        return self._value

    @property
    def in_plain_english(self) -> str:
        return LABELS.english.get(self.value) or "???"


class CompoundLinguisticTag(LinguisticTag):
    def __init__(self, tags: Iterable[FSTTag]) -> None:
        self._fst_tags = tuple(tags)

    @property
    def value(self):
        return "".join(self._fst_tags)

    @property
    def in_plain_english(self):
        return LABELS.english.get_longest(self._fst_tags)


def linguistic_tag_from_fst_tags(tags: Tuple[FSTTag, ...]) -> LinguisticTag:
    """
    Returns the appropriate LinguisticTag, no matter how many tags you chuck at it!
    """
    assert len(tags) > 0
    if len(tags) == 1:
        return SimpleLinguisticTag(tags[0])
    else:
        return CompoundLinguisticTag(tags)
