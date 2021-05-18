"""
this file contains `TypedDict` classes that effectively serves as json schema for serialized objects
"""
from typing import List, Tuple, Union, Optional, Sequence

from typing_extensions import Literal, TypedDict

from CreeDictionary.utils.types import FSTTag


class SerializedDefinition(TypedDict):
    text: str
    source_ids: Sequence[str]


class SerializedWordform(TypedDict):
    id: int
    text: str
    inflectional_category: str
    pos: str
    analysis: str
    is_lemma: bool
    as_is: bool
    lemma: int  # the id of the lemma

    # ---- calculated properties ----
    lemma_url: str

    # ---- informational properties ----
    inflectional_category_plain_english: str
    inflectional_category_linguistic: str
    wordclass_emoji: str
    wordclass: str

    # ---- foreign keys ----
    definitions: List[SerializedDefinition]


class SerializedLinguisticTag(TypedDict):
    # The tag in its original form, e.g., from the FST
    value: str

    # The value of the feature, written in plain English
    in_plain_english: str


class SerializedSearchResult(TypedDict):
    # the text of the match
    wordform_text: str
    # legacy name, deprecated
    matched_cree: Optional[str]

    is_lemma: bool

    matched_by: Literal["ENGLISH", "CREE"]

    # The matched lemma
    lemma_wordform: SerializedWordform

    # triple dots in type annotation means they can have zero or more elements

    # user friendly linguistic breakdowns
    linguistic_breakdown_head: Tuple[str, ...]
    linguistic_breakdown_tail: Tuple[str, ...]

    # The suffix tags, straight from the FST
    raw_suffix_tags: Tuple[FSTTag, ...]

    # Sequence of all preverb tags, in order
    # Optional: we might not have some preverbs in our database
    preverbs: Tuple[Union[str, SerializedWordform], ...]

    # This omits preverbs and other features displayed elsewhere
    relevant_tags: Tuple[SerializedLinguisticTag, ...]

    definitions: Tuple[SerializedDefinition, ...]
