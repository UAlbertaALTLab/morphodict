from __future__ import annotations

import dataclasses
import json
import re

from dataclasses import dataclass, field
from enum import Enum
from typing import NewType, Optional, Protocol, cast, Iterable, Tuple
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset, Lemma as WNLemma
from collections.abc import Iterable

from morphodict.utils.serializer import SerializedLinguisticTag
from morphodict.utils.types import FSTTag, Label
from morphodict.lexicon.models import Wordform, wordform_cache
from morphodict.search import ranking
from morphodict.relabelling import LABELS


Preverb = Wordform
Lemma = NewType("Lemma", Wordform)
MatchedEnglish = NewType("MatchedEnglish", str)
InternalForm = NewType("InternalForm", str)


class LinguisticTag(Protocol):
    """
    A linguistic feature/tag pair.
    """

    @property
    def value(self) -> FSTTag: ...

    # TODO: linguistic feature

    @property
    def in_plain_english(self) -> str: ...

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
        return cast(str, LABELS.english.get(self.value, cast(Label, self.value)))


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


class Language(Enum):
    SOURCE = "Source"
    TARGET = "Target"


@dataclass
class Result:
    """
    A target-language wordform and the features that link it to a query.

    Features of a wordform allow better inferences about how good a result is.

    Some examples of these features could include:
      - Is this Result a match between a source-language query and wordform
        text, or between a target-language query term and a word in the
        definition text?
      - What is the edit distance between the query term and the wordform?
      - What is the best cosine vector distance between a definition of the
        result wordform and the query terms?

    The best search results will presumably have better scores on more features
    of greater importance.

    Search methods may generate candidate results that are ultimately not sent
    to users, so any user-friendly tagging/relabelling is instead done in
    PresentationResult class.
    """

    def __post_init__(self):
        if all(
            getattr(self, field.name) in (None, [])
            for field in dataclasses.fields(Result)
            if field.init and field.name != "wordform"
        ):
            raise Exception("No features were provided for why this is a result.")

        self.is_lemma = self.wordform.is_lemma
        self.lemma_wordform = self.wordform.lemma
        self.wordform_length = len(self.wordform.text)

        self.pos_match = self.pos_match
        self.glossary_count = self.glossary_count
        self.lemma_freq = self.lemma_freq

        if self.did_match_source_language and self.query_wordform_edit_distance is None:
            raise Exception("must include edit distance on source language matches")

        if self.morpheme_ranking is None:
            # todo: normalize morpheme ranking by dividing by max value
            self.morpheme_ranking = wordform_cache.MORPHEME_RANKINGS.get(
                self.wordform.text, None
            ) or wordform_cache.MORPHEME_RANKINGS.get(self.lemma_wordform.text, None)

        if rich_analysis := self.lemma_wordform.analysis:
            self.lemma_morphemes = rich_analysis.generate_with_morphemes(
                self.lemma_wordform.text
            )

    def add_features_from(self, other: Result):
        """Add the features from `other` into this object

        Good results can match for many different reasons. This method merges
        features from a different result object for the same wordform into the
        current object.
        """
        assert self.wordform.key == other.wordform.key
        self._copy_features_from(other)

    def _copy_features_from(self, other: Result):
        for field_name, other_value in other.features().items():
            if other_value is not None:
                self_value = getattr(self, field_name)
                # combine lists, applying uniq
                if isinstance(self_value, list):
                    self_value[:] = list(set(self_value + other_value))
                elif (
                    field_name == "cosine_vector_distance"
                    and self.cosine_vector_distance is not None
                    # We already checked that other.cosine_vector_distance is
                    # not None, but mypy can’t infer that.
                    and other.cosine_vector_distance is not None
                ):
                    self.cosine_vector_distance = min(
                        self.cosine_vector_distance, other.cosine_vector_distance
                    )
                elif field_name == "query_wordform_edit_distance":
                    self.query_wordform_edit_distance = min(
                        v
                        for v in (
                            self.query_wordform_edit_distance,
                            other.query_wordform_edit_distance,
                        )
                        if v is not None
                    )
                else:
                    setattr(self, field_name, other_value)

    def create_related_result(self, new_wordform, **kwargs):
        """Create a new Result for new_wordform, with features copied over."""

        # Note: we can’t use dataclasses.replace because it does shallow copies
        # and we have list members.

        # TODO: write tests for this

        new_result = Result(new_wordform, **kwargs)
        new_result._copy_features_from(self)
        # That copy may have overwritten some features supplied in kwargs
        for k, v in kwargs.items():
            setattr(new_result, k, v)
        new_result.__post_init__()
        return new_result

    wordform: Wordform
    lemma_wordform: Lemma = field(init=False)
    is_lemma: bool = field(init=False)
    wordform_length: int = field(init=False)
    lemma_morphemes: Optional[list] = None

    #: What, if any, was the matching string?
    source_language_match: Optional[str] = None
    query_wordform_edit_distance: Optional[float] = None

    source_language_affix_match: Optional[bool] = None
    target_language_affix_match: Optional[bool] = None

    target_language_keyword_match: list[str] = field(default_factory=list)

    analyzable_inflection_match: Optional[bool] = None

    source_language_keyword_match: list[str] = field(default_factory=list)

    is_espt_result: Optional[bool] = None

    pos_match: Optional[int] = None
    glossary_count: Optional[int] = None
    lemma_freq: Optional[int] = None

    #: Was anything in the query a target-language match for this result?
    did_match_target_language: Optional[bool] = None

    morpheme_ranking: Optional[float] = None

    cosine_vector_distance: Optional[float] = None

    relevance_score: Optional[float] = None

    target_language_wordnet_match: list[str] = field(default_factory=list)

    def features(self):
        ret = {}
        for field in dataclasses.fields(Result):
            if field.name in [
                "target_language_keyword_match",
                "morpheme_ranking",
                "glossary_count",
                "lemma_freq",
                "pos_match",
                "cosine_vector_distance",
                "relevance_score",
            ]:
                value = getattr(self, field.name)
                ret[field.name] = value
        return ret

    def features_json(self):
        return json.dumps(
            self.features(),
            ensure_ascii=False,
            indent=2,
        )

    #: Was anything in the query a source-language match for this result?
    @property
    def did_match_source_language(self) -> bool:
        return bool(
            self.source_language_match
            or self.source_language_affix_match is not None
            or self.analyzable_inflection_match
            or self.source_language_keyword_match
        )

    # This is a separate method instead of a magic cached property because:
    #  1. When experimenting with ranking methods, completely unrelated code
    #     might want to set a relevance score.
    #  2. While we want the relevance score to be cached for sorting, it
    #     should also be invalidated if the object is mutated. For now code
    #     that uses Result lists is responsible for calling this method
    #     explicitly when done adding results.
    #  3. Dataclasses make doing custom caching a little trickier
    def assign_default_relevance_score(self):
        ranking.assign_relevance_score(self)

    def __lt__(self, other: Result):
        assert self.relevance_score is not None
        assert other.relevance_score is not None
        return self.relevance_score > other.relevance_score

    def __str__(self):
        return f"Result<wordform={self.wordform}>"


format_regexp = r"^\s*\((?P<pos>\w+)\)\s+(?P<stem>.+)\s*\#\s*(?P<num>\d+)\s*\Z"


def wordnet_for_nltk(keyword: str) -> str:
    matches = re.match(format_regexp, keyword)
    if matches:
        return (
            "_".join([x for x in matches["stem"].split(" ") if x])
            + "."
            + matches["pos"]
            + "."
            + matches["num"]
        )
    return keyword


class WordnetEntry:

    synset: Synset
    original_str: str
    numbering: Optional[int]

    def __init__(self, entry: str | Synset):
        if isinstance(entry, str):
            self.synset = wn.synset(wordnet_for_nltk(entry))
            self.original_str = entry
        else:
            self.synset = entry
            self.original_str = entry.name()

    def __str__(self):
        data = self.synset.name().split(".")
        entry = ".".join(data[0:-2])
        return f"({data[-2]}) {entry}#{int(data[-1])}"

    def hyponyms(self) -> list[WordnetEntry]:
        return produce_entries(self.original_str, self.synset.hyponyms())

    def hypernyms(self) -> list[WordnetEntry]:
        return produce_entries(self.original_str, self.synset.hyponyms())

    def member_holonyms(self) -> list[WordnetEntry]:
        return produce_entries(self.original_str, self.synset.member_holonyms())

    def definition(self) -> str:
        return self.synset.definition()

    def heading(self) -> str:
        return self.synset.lemmas()[0].name() + f" ({self.synset.pos()})"

    def pos(self) -> str:
        return self.synset.pos()

    def paren_pos(self) -> str:
        return f"({self.synset.pos()})"

    def synonyms(self) -> list[str]:
        return [" ".join(l.name().split("_")) for l in self.synset.lemmas()]

    def lemmas(self) -> list[WNLemma]:
        return self.synset.lemmas()

    def ranking(self) -> int:
        return sum([l.count() for l in self.synset.lemmas()])

    def nltk_name(self) -> str:
        return self.synset.name()

    def sources(self) -> list[str]:
        return ["WN"]


def produce_entries(origin: str, entries: Iterable[Synset]) -> list[WordnetEntry]:
    ans = [WordnetEntry(e) for e in entries]
    for e in ans:
        e.original_str = origin
    return ans
