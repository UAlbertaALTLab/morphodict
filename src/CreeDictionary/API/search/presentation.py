from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, TypedDict, Iterable, Any, cast, Dict, Literal

from django.forms import model_to_dict

from CreeDictionary.utils import get_modified_distance
from CreeDictionary.API.search import types, core, lookup
from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from CreeDictionary.CreeDictionary.relabelling import read_labels
from CreeDictionary.utils.types import FSTTag, Label, ConcatAnalysis
from morphodict.analysis import RichAnalysis
from .types import Preverb, LinguisticTag, linguistic_tag_from_fst_tags
from morphodict.lexicon.models import Wordform, wordform_cache
from ..schema import SerializedWordform, SerializedDefinition, SerializedLinguisticTag

class AbstractResult:
    def serialize(self):
        return {
            "text": self.text,
            "definitions": self.definitions,
        }

@dataclass
class _ReduplicationResult(AbstractResult):
    """Tiny class to mimic the format of preverbs"""

    text: str
    definitions: list


@dataclass
class _InitialChangeResult(AbstractResult):
    """Tiny class to mimic the format of preverbs"""

    text: str
    definitions: list



LexicalEntryType = Literal["Preverb", "Reduplication", "Initial Change"]


@dataclass
class _LexicalEntry:
    entry: _ReduplicationResult | SerializedWordform | _InitialChangeResult
    type: LexicalEntryType
    original_tag: FSTTag


class SerializedPresentationResult(TypedDict):
    lemma_wordform: SerializedWordform
    wordform_text: str
    is_lemma: bool
    definitions: Iterable[SerializedDefinition]
    lexical_info: List[Dict]
    preverbs: Iterable[SerializedWordform]
    friendly_linguistic_breakdown_head: Iterable[Label]
    friendly_linguistic_breakdown_tail: Iterable[Label]
    relevant_tags: Iterable[SerializedLinguisticTag]


class PresentationResult:
    """
    A result ready for user display, and serializable for templates

    The non-presentation Result class is used for gathering features and ranking
    results. When the results to show have been decided upon, this class adds
    presentation things like labels.
    """

    def __init__(self, result: types.Result, *, search_run: core.SearchRun):
        self._result = result
        self._search_run = search_run

        self.wordform = result.wordform
        self.lemma_wordform = result.lemma_wordform
        self.is_lemma = result.is_lemma
        self.source_language_match = result.source_language_match

        (
            self.linguistic_breakdown_head,
            _,
            self.linguistic_breakdown_tail,
        ) = result.wordform.analysis or [[], None, []]

        self.lexical_info = get_lexical_info(result.wordform.analysis)

        self.preverbs = [
            lexical_entry["entry"]
            for lexical_entry in self.lexical_info
            if lexical_entry["type"] == "Preverb"
        ]
        self.reduplication = [
            lexical_entry["entry"]
            for lexical_entry in self.lexical_info
            if lexical_entry["type"] == "Reduplication"
        ]

        self.friendly_linguistic_breakdown_head = replace_user_friendly_tags(
            list(t.strip("+") for t in self.linguistic_breakdown_head)
        )
        self.friendly_linguistic_breakdown_tail = replace_user_friendly_tags(
            list(t.strip("+") for t in self.linguistic_breakdown_tail)
        )

    def serialize(self) -> SerializedPresentationResult:
        ret: SerializedPresentationResult = {
            "lemma_wordform": serialize_wordform(self.lemma_wordform),
            "wordform_text": self.wordform.text,
            "is_lemma": self.is_lemma,
            "definitions": serialize_definitions(
                self.wordform.definitions.all(),
                # This is the only place include_auto_definitions is used,
                # because we only auto-translate non-lemmas, and this is the
                # only place where a non-lemma search result appears.
                include_auto_definitions=self._search_run.include_auto_definitions,
            ),
            "lexical_info": self.lexical_info,
            "preverbs": self.preverbs,
            "friendly_linguistic_breakdown_head": self.friendly_linguistic_breakdown_head,
            "friendly_linguistic_breakdown_tail": self.friendly_linguistic_breakdown_tail,
            "relevant_tags": tuple(t.serialize() for t in self.relevant_tags),
        }
        if self._search_run.query.verbose:
            cast(Any, ret)["verbose_info"] = self._result

        return ret

    @property
    def relevant_tags(self) -> Tuple[LinguisticTag, ...]:
        """
        Tags and features to display in the linguistic breakdown pop-up.
        This omits preverbs and other features displayed elsewhere

        In itwêwina, these tags are derived from the suffix features exclusively.
        We chunk based on the English relabelleings!
        """
        return tuple(
            linguistic_tag_from_fst_tags(tuple(cast(FSTTag, t) for t in fst_tags))
            for fst_tags in read_labels().english.chunk(
                t.strip("+") for t in self.linguistic_breakdown_tail
            )
        )

    def __str__(self):
        return f"PresentationResult<{self.wordform}:{self.wordform.id}>"


def serialize_wordform(wordform) -> SerializedWordform:
    """
    Intended to be passed in a JSON API or into templates.

    :return: json parsable result
    """
    result = model_to_dict(wordform)
    result["definitions"] = serialize_definitions(wordform.definitions.all())
    result["lemma_url"] = wordform.get_absolute_url()

    if wordform.linguist_info:
        if inflectional_category := wordform.linguist_info.get(
            "inflectional_category", None
        ):
            result.update(
                {
                    "inflectional_category_plain_english": read_labels().english.get(
                        inflectional_category
                    ),
                    "inflectional_category_linguistic": read_labels().linguistic_long.get(
                        inflectional_category
                    ),
                }
            )
        if wordclass := wordform.linguist_info.get("wordclass"):
            result["wordclass_emoji"] = get_emoji_for_cree_wordclass(wordclass)

    for key in wordform.linguist_info or []:
        if key not in result:
            result[key] = wordform.linguist_info[key]

    return result


def serialize_definitions(definitions, include_auto_definitions=False):
    ret = []
    for definition in definitions:
        serialized = definition.serialize()
        if include_auto_definitions or "auto" not in serialized["source_ids"]:
            ret.append(serialized)
    return ret


def serialize_lexical_entry(lexical_entry: _LexicalEntry) -> dict:
    return {
        "entry": lexical_entry.entry,
        "type": lexical_entry.type,
        "original_tag": lexical_entry.original_tag,
    }


def safe_partition_analysis(analysis: ConcatAnalysis):
    try:
        (
            linguistic_breakdown_head,
            _,
            linguistic_breakdown_tail,
        ) = partition_analysis(analysis)
    except ValueError:
        linguistic_breakdown_head = []
        linguistic_breakdown_tail = []
    return linguistic_breakdown_head, linguistic_breakdown_tail


def replace_user_friendly_tags(fst_tags: List[FSTTag]) -> List[Label]:
    """replace fst-tags to cute ones"""
    return read_labels().english.get_full_relabelling(fst_tags)


def get_emoji_for_cree_wordclass(word_class: Optional[str]) -> Optional[str]:
    """
    Attempts to get an emoji description of the full wordclass.
    e.g., "👤👵🏽" for "nôhkom"
    """
    if word_class is None:
        return None

    def to_fst_output_style(value):
        if value[0] == "N":
            return list(value.upper())
        elif value[0] == "V":
            return ["V", value[1:].upper()]
        else:
            return [value.title()]

    tags = to_fst_output_style(word_class)
    return read_labels().emoji.get_longest(tags)


def get_lexical_info(result_analysis: RichAnalysis) -> List[Dict]:
    if not result_analysis:
        return []

    result_analysis_tags = result_analysis.prefix_tags
    first_letters = extract_first_letters(result_analysis)

    lexical_info: List[Dict] = []

    for (i, tag) in enumerate(result_analysis_tags):
        preverb_result: Optional[Preverb] = None
        reduplication_string: Optional[str] = None
        _type: Optional[LexicalEntryType] = None
        entry: Optional[_ReduplicationResult | SerializedWordform | _InitialChangeResult] = None

        if tag in ["RdplW+", "RdplS+"]:
            reduplication_string = generate_reduplication_string(
                tag, first_letters[i + 1]
            )

        elif tag == "IC+":
            change_types = get_initial_change_types()
            _type = "Initial Change"
            entry = _InitialChangeResult(
                text=" ",
                definitions=change_types
            ).serialize()

        elif tag.startswith("PV/"):
            # use altlabel.tsv to figure out the preverb

            # ling_short looks like: "Preverb: âpihci-"
            ling_short = read_labels().linguistic_short.get(
                cast(FSTTag, tag.rstrip("+"))
            )
            if ling_short:
                # convert to "âpihci" by dropping prefix and last character
                normative_preverb_text = ling_short[len("Preverb: ") :]
                preverb_results = Wordform.objects.filter(
                    text=normative_preverb_text, raw_analysis__isnull=True
                )

                # find the one that looks the most similar
                if preverb_results:
                    preverb_result = min(
                        preverb_results,
                        key=lambda pr: get_modified_distance(
                            normative_preverb_text,
                            pr.text.strip("-"),
                        ),
                    )

                else:
                    # Can't find a match for the preverb in the database.
                    # This happens when searching against the test database for
                    # ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk, as the test database
                    # lacks lacks ê and kî.
                    preverb_result = Wordform(
                        text=normative_preverb_text, is_lemma=True
                    )

        if reduplication_string is not None:
            entry = _ReduplicationResult(
                text=reduplication_string,
                definitions=[
                    {
                        "text": "Strong reduplication"
                        if tag == "RdplS+"
                        else "Weak Reduplication"
                    }
                ],
            ).serialize()
            _type = "Reduplication"

        if preverb_result is not None:
            entry = serialize_wordform(preverb_result)
            _type = "Preverb"

        if entry and _type:
            result = _LexicalEntry(entry=entry, type=_type, original_tag=tag)
            lexical_info.append(serialize_lexical_entry(result))

    return lexical_info


def extract_first_letters(analysis: RichAnalysis) -> List[str]:
    """
    Returns the first letter of Plains Cree FST preverb tags, as well as the.

    For example, "ê-kâh-kîmôci-kotiskâwêyahk", you have the following analysis:

    >>> a = RichAnalysis((("PV/e+", "RdplS+", "PV/nitawi+"), "kotiskâwêw", ("+V", "+AI", "+Cnj", "+12Pl")))

    Then extracting the first letters of the preverbs and lemma:

    >>> extract_first_letters(a)
    ['e', 'R', 'n', 'k']

    Note: the Plains Cree FST preverb tags (PV/*) do not contain long vowel diacrictics;
    that is "ê-" is represented as "PV/e". Luckily, this doesn't matter, since the
    reduplication for any vowel is always either "ay-" or "âh-"!

    """
    tags = analysis.prefix_tags + (analysis.lemma,)

    def first_letter(x):
        pieces = x.split("/")
        return pieces[-1][0]

    return [first_letter(t) for t in tags]


def generate_reduplication_string(tag: str, letter: str) -> str:
    consonants = "chkmnpstwy"
    reduplication_string = ""
    if tag == "RdplW+":
        reduplication_string = letter + "a-" if letter.lower() in consonants else "ay-"
    elif tag == "RdplS+":
        reduplication_string = letter + "âh-" if letter.lower() in consonants else "âh-"

    return reduplication_string


def get_initial_change_types() -> List[dict[str, str]]:
    return [{ "text": '\n'.join(["a → ê", "i → ê", "o → wê", "ê → iyê", "â → iyâ", "î → â / iyî", "ô → iyô"]) }]
