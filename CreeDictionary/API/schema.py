"""
this file contains `TypedDict` classes that effectively serves as json schema for serialized objects
"""
from typing import List, Tuple, Union
from typing_extensions import TypedDict, Literal


class SerializedDefinition(TypedDict):
    text: str
    source_ids: Tuple[str]


class SerializedWordform(TypedDict):
    id: int
    text: str
    full_lc: str
    pos: str
    analysis: str
    is_lemma: bool
    as_is: bool
    lemma: int  # the id of the lemma

    # ---- calculated properties ---
    lemma_url: str

    # ---- foreign keys ----
    definition: List[SerializedDefinition]


class SerializedSearchResult(TypedDict):
    # the text of the match
    matched_cree: str

    is_lemma: bool

    matched_by: Literal["ENGLISH", "CREE"]

    # The matched lemma
    lemma_wordform: SerializedWordform

    # triple dots in type annotation means they can have zero or more elements

    # user friendly linguistic breakdowns
    linguistic_breakdown_head: Tuple[str, ...]
    linguistic_breakdown_tail: Tuple[str, ...]

    # Sequence of all preverb tags, in order
    # Optional: we might not have some preverbs in our database
    preverbs: Tuple[Union[str, SerializedWordform], ...]

    # TODO: there are things to be figured out for this :/
    # Sequence of all reduplication tags present, in order
    reduplication_tags: Tuple[str, ...]
    # Sequence of all initial change tags
    initial_change_tags: Tuple[str, ...]

    definitions: Tuple[SerializedDefinition, ...]
