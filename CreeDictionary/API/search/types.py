from typing import NamedTuple, Union, Set, NewType, Iterable, Tuple, cast

import attr
from attr import attrs

from typing_extensions import Protocol

from API.helpers import serialize_definitions
from API.models import Wordform, Definition
from API.schema import SerializedLinguisticTag, SerializedSearchResult
from utils import Language
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


@attrs(auto_attribs=True, frozen=True)  # frozen makes it hashable
class SearchResult:
    """
    Contains all of the information needed to display a search result.

    Comment:
    Each instance corresponds visually to one card shown on the interface
    """

    # the text of the match
    matched_cree: str

    is_lemma: bool

    # English or Cree
    matched_by: Language

    # The matched lemma
    lemma_wordform: Wordform

    # triple dots in type annotation means they can be empty

    # user friendly linguistic breakdowns
    linguistic_breakdown_head: Tuple[str, ...]
    linguistic_breakdown_tail: Tuple[str, ...]

    # The suffix tags, straight from the FST
    raw_suffix_tags: Tuple[FSTTag, ...]

    # Sequence of all preverb tags, in order
    # Optional: we might not have some preverbs in our database
    preverbs: Tuple[Preverb, ...]

    # TODO: there are things to be figured out for this :/
    # Sequence of all reduplication tags present, in order
    reduplication_tags: Tuple[str, ...]
    # Sequence of all initial change tags
    initial_change_tags: Tuple[str, ...]

    definitions: Tuple[Definition, ...]

    def serialize(self, include_auto_definitions) -> SerializedSearchResult:
        """
        serialize the instance, can be used before passing into a template / in an API view, etc.
        """
        # note: passing in serialized "dumb" object instead of smart ones to templates is a Django best practice
        # it avoids unnecessary database access and makes APIs easier to create
        result = attr.asdict(self)
        # lemma field will refer to lemma_wordform itself, which makes it impossible to serialize
        result["lemma_wordform"] = self.lemma_wordform.serialize(
            include_auto_definitions=include_auto_definitions
        )

        result["preverbs"] = []
        for pv in self.preverbs:
            if isinstance(pv, str):
                result["preverbs"].append(pv)
            else:  # Wordform
                result["preverbs"].append(
                    pv.serialize(include_auto_definitions=include_auto_definitions)
                )

        result["matched_by"] = self.matched_by.name
        result["definitions"] = serialize_definitions(
            self.definitions, include_auto_definitions
        )
        result["relevant_tags"] = tuple(t.serialize() for t in self.relevant_tags)

        return cast(SerializedSearchResult, result)

    @property
    def relevant_tags(self) -> Tuple[LinguisticTag, ...]:
        """
        Tags and features to display in the linguistic breakdown pop-up.
        This omits preverbs and other features displayed elsewhere

        In itwêwina, these tags are derived from the suffix features exclusively.
        We chunk based on the English relabelleings!
        """
        return tuple(
            linguistic_tag_from_fst_tags(fst_tags)
            for fst_tags in LABELS.english.chunk(self.raw_suffix_tags)
        )
