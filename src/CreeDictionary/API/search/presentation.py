from __future__ import annotations

from typing import List, Tuple, Optional, TypedDict, Iterable, Any, cast

from django.forms import model_to_dict

from CreeDictionary.utils import get_modified_distance
from . import types, core, lookup
from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from CreeDictionary.CreeDictionary.relabelling import read_labels
from CreeDictionary.utils.types import FSTTag, Label, ConcatAnalysis
from .types import Preverb, LinguisticTag, linguistic_tag_from_fst_tags
from morphodict.lexicon.models import Wordform, wordform_cache
from ..schema import SerializedWordform, SerializedDefinition, SerializedLinguisticTag


class SerializedPresentationResult(TypedDict):
    lemma_wordform: SerializedWordform
    wordform_text: str
    is_lemma: bool
    definitions: Iterable[SerializedDefinition]
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

        analysis = result.wordform.analysis or [[], None, []]
        (
            self.linguistic_breakdown_head,
            _,
            self.linguistic_breakdown_tail,
        ) = analysis

        self.preverbs = get_preverbs_from_head_breakdown(self.linguistic_breakdown_head)

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
            "preverbs": [serialize_wordform(pv) for pv in self.preverbs],
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

            result["inflectional_category_plain_english"] = read_labels().english.get(
                inflectional_category
            )
            result[
                "inflectional_category_linguistic"
            ] = read_labels().linguistic_long.get(inflectional_category)
        if wordclass := wordform.linguist_info.get("wordclass"):
            result["wordclass"] = wordclass
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
            return "+" + "+".join(list(value.upper()))
        elif value[0] == "V":
            return "+" + "+".join(["V", value[1:].upper()])
        else:
            return "+" + value.title()

    fst_tag_str = to_fst_output_style(word_class).strip("+")
    tags = [FSTTag(t) for t in fst_tag_str.split("+")]
    return read_labels().emoji.get_longest(tags)


def get_preverbs_from_head_breakdown(
    head_breakdown: List[FSTTag],
) -> Tuple[Preverb, ...]:
    results = []

    for tag in head_breakdown:
        preverb_result: Optional[Preverb] = None
        if tag.startswith("PV/"):
            # use altlabel.tsv to figure out the preverb

            # ling_short looks like: "Preverb: âpihci-"
            ling_short = read_labels().linguistic_short.get(
                cast(FSTTag, tag.rstrip("+"))
            )
            if ling_short is not None and ling_short != "":
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

        if preverb_result is not None:
            results.append(preverb_result)
    return tuple(results)
