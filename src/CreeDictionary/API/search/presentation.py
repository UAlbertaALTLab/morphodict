from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, Optional, TypedDict, cast, Tuple

from django.conf import settings
from django.forms import model_to_dict

from CreeDictionary.API.search import core, types
from morphodict.relabelling import read_labels, LABELS
from CreeDictionary.utils import get_modified_distance
from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from .types import Preverb, LinguisticTag, linguistic_tag_from_fst_tags
from CreeDictionary.utils.types import ConcatAnalysis, FSTTag, Label
from crkeng.app.preferences import (
    DisplayMode,
    AnimateEmoji,
    DictionarySource,
    ShowEmoji,
)
from morphodict.analysis import RichAnalysis
from morphodict.lexicon.models import Wordform, SourceLanguageKeyword

from ..schema import SerializedDefinition, SerializedWordform, SerializedLinguisticTag
from .types import Preverb


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
    entry: List[_ReduplicationResult | SerializedWordform | _InitialChangeResult]
    text: Optional[str]
    url: str
    id: str | int | None
    type: LexicalEntryType
    original_tag: FSTTag


class SerializedPresentationResult(TypedDict):
    lemma_wordform: SerializedWordform
    wordform_text: str
    is_lemma: bool
    definitions: Iterable[SerializedDefinition]
    lexical_info: List
    preverbs: Iterable[SerializedWordform]
    friendly_linguistic_breakdown_head: Iterable[Label]
    friendly_linguistic_breakdown_tail: Iterable[Label]
    relevant_tags: Iterable[SerializedLinguisticTag]
    morphemes: Optional[Iterable[str]]
    lemma_morphemes: Optional[Iterable[str]]
    # Maps a display mode to relabellings
    relabelled_fst_analysis: list[SerializedRelabelling]
    relabelled_linguist_analysis: str
    show_form_of: bool


class SerializedRelabelling(TypedDict):
    """
    A relabelled "chunk". This might be one or more tags from the FST analysis.

    Examples:
         - {"tags": ["+N", "+A"], label": "animate noun"}
         - {"tags": ["+Sg"], label": "singular"}
         - {"tags": ["+V", "+T", "+A"], label": "animate transitive verb"}
         - {"tags": ["+Obv"], label": "obviative"}
    """

    tags: list[FSTTag]
    label: str


class PresentationResult:
    """
    A result ready for user display, and serializable for templates

    The non-presentation Result class is used for gathering features and ranking
    results. When the results to show have been decided upon, this class adds
    presentation things like labels.
    """

    def __init__(
        self,
        result: types.Result,
        *,
        search_run: core.SearchRun,
        display_mode="community",
        animate_emoji=AnimateEmoji.default,
        show_emoji=ShowEmoji.default,
        dict_source=None,
    ):
        self._result = result
        self._search_run = search_run
        self._relabeller = {
            "english": read_labels().english,
            "linguistic": read_labels().linguistic_long,
            "source_language": read_labels().source_language,
        }.get(display_mode, DisplayMode.default)
        self._animate_emoji = animate_emoji
        self._show_emoji = show_emoji

        self.wordform = result.wordform
        self.lemma_wordform = result.lemma_wordform
        self.is_lemma = result.is_lemma
        self.source_language_match = result.source_language_match
        self.dict_source = dict_source

        if settings.MORPHODICT_TAG_STYLE == "Plus":
            (
                self.linguistic_breakdown_head,
                _,
                self.linguistic_breakdown_tail,
            ) = result.wordform.analysis or [[], None, []]
        elif settings.MORPHODICT_TAG_STYLE == "Bracket":
            # Arapaho has some head tags that the Plus-style FSTs put at the
            # tail. For now, move them; later on elaboration could be a
            # language-specific function.
            head, _, tail = result.wordform.analysis or [[], None, []]

            new_head = []
            new_tail_prefix = []
            for i, tag in enumerate(head):
                if tag.startswith("["):
                    new_tail_prefix.append(tag)
                else:
                    new_head.append(tag)
            self.linguistic_breakdown_head = new_head
            self.linguistic_breakdown_tail = new_tail_prefix + list(tail)
        else:
            raise Exception(f"Unknown {settings.MORPHODICT_TAG_STYLE=}")

        self.lexical_info = get_lexical_info(
            result.wordform.analysis, animate_emoji, self._show_emoji, self.dict_source
        )

        if rich_analysis := result.wordform.analysis:
            self.morphemes = rich_analysis.generate_with_morphemes(result.wordform.text)
        else:
            self.morphemes = None

        self.lemma_morphemes = result.lemma_morphemes

        self.lexical_info = get_lexical_info(
            result.wordform.analysis,
            animate_emoji=animate_emoji,
            dict_source=self.dict_source,
            show_emoji=self._show_emoji,
        )

        self.preverbs: List[SerializedWordform] = [
            cast(SerializedWordform, entry)
            for lexical_entry in self.lexical_info
            for entry in lexical_entry["entry"]
            if lexical_entry["type"] == "Preverb"
        ]
        self.reduplication = [
            lexical_entry["entry"]
            for lexical_entry in self.lexical_info
            if lexical_entry["type"] == "Reduplication"
        ]

        self.friendly_linguistic_breakdown_head = replace_user_friendly_tags(
            to_list_of_fst_tags(self.linguistic_breakdown_head)
        )
        self.friendly_linguistic_breakdown_tail = replace_user_friendly_tags(
            to_list_of_fst_tags(self.linguistic_breakdown_tail)
        )

    def serialize(self) -> SerializedPresentationResult:
        ret: SerializedPresentationResult = {
            "lemma_wordform": serialize_wordform(
                self.lemma_wordform,
                self._animate_emoji,
                self._show_emoji,
                self.dict_source,
            ),
            "wordform_text": self.wordform.text,
            "is_lemma": self.is_lemma,
            "definitions": serialize_definitions(
                # given changes in django 4.1, the previous approach can fail.
                # check first that the wordform actually exists before trying to get the reverse manager.
                (
                    self.wordform.definitions.all()
                    if not self.wordform._state.adding
                    else []
                ),
                # This is the only place include_auto_definitions is used,
                # because we only auto-translate non-lemmas, and this is the
                # only place where a non-lemma search result appears.
                include_auto_definitions=self._search_run.include_auto_definitions,
                dict_source=self.dict_source,
            ),
            "lexical_info": self.lexical_info,
            "preverbs": self.preverbs,
            "friendly_linguistic_breakdown_head": self.friendly_linguistic_breakdown_head,
            "friendly_linguistic_breakdown_tail": self.friendly_linguistic_breakdown_tail,
            "relabelled_fst_analysis": self.relabelled_fst_analysis,
            "relabelled_linguist_analysis": self.relabelled_linguist_analysis,
            "show_form_of": should_show_form_of(
                self.is_lemma,
                self.lemma_wordform,
                self.dict_source,
                self._search_run.include_auto_definitions,
            ),
            "relevant_tags": tuple(t.serialize() for t in self.relevant_tags),
            "morphemes": self.morphemes,
            "lemma_morphemes": self.lemma_morphemes,
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
            for fst_tags in LABELS.english.chunk(
                t.strip("+") for t in self.linguistic_breakdown_tail
            )
        )

    @property
    def relabelled_fst_analysis(self) -> list[SerializedRelabelling]:
        """
        Returns a list of relabellings for the suffix tags from the FST analysis.
        The relabellings are returned according to the current display mode.

        Note: how the tags get chunked may change **depending on the display mode**!
        That is, relabellings in one display mode might produce different relabelled
        chunks in a different display mode! It is not safe to create parallel arrays.
        """

        all_tags = to_list_of_fst_tags(self.linguistic_breakdown_tail)
        results: list[SerializedRelabelling] = []

        for tags in self._relabeller.chunk(all_tags):
            label = self._relabeller.get_longest(tags)

            if label is None:
                print(f"Warning: no label for tag chunk {tags!r}")
                label = " ".join(tags)

            results.append({"tags": list(tags), "label": str(label)})

        return results

    @property
    def relabelled_linguist_analysis(self) -> str:
        try:
            analysis = self.lemma_wordform.linguist_info["analysis"]
            pattern = "<td>(.*?)</td>"
            info = re.findall(pattern, analysis)
            cleaned_info = []
            for i in info:
                if "<b>" in i:
                    j = i.replace("<b>", "").replace("</b>", "")
                else:
                    j = i
                cleaned_info.append(j)
            relabelled = []
            for c in cleaned_info:
                if self._relabeller.get(c):
                    relabelled.append(self._relabeller.get(c))
                else:
                    relabelled.append(c)

            k = 0
            while k < len(cleaned_info):
                analysis = analysis.replace(cleaned_info[k], relabelled[k])
                k += 1
            return analysis
        except:
            return ""

    def __str__(self):
        return f"PresentationResult<{self.wordform}:{self.wordform.id}>"


def should_show_form_of(
    is_lemma, lemma_wordform, dict_source, include_auto_definitions
):
    if not dict_source or dict_source == ["ALL"]:
        return True
    if is_lemma:
        return True
    for definition in lemma_wordform.definitions.all():
        for source in definition.source_ids:
            if source in dict_source:
                return True
            elif include_auto_definitions and source.replace("🤖", "") in dict_source:
                return True
    return False


def serialize_wordform(
    wordform: Wordform, animate_emoji: str, show_emoji: str, dict_source: list
) -> SerializedWordform:
    """
    Intended to be passed in a JSON API or into templates.

    :return: json parsable result
    """
    result = model_to_dict(wordform)
    result["definitions"] = serialize_definitions(
        wordform.definitions.all(), dict_source=dict_source
    )
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
            result["wordclass_emoji"] = get_emoji_for_cree_wordclass(
                wordclass, animate_emoji
            )
    result["show_emoji"] = True if show_emoji == "yes" else False

    for key in wordform.linguist_info or []:
        if key not in result:
            result[key] = wordform.linguist_info[key]

    return cast(SerializedWordform, result)


def serialize_definitions(
    definitions, include_auto_definitions=False, dict_source=None
):
    ret = []
    for definition in definitions:
        serialized = definition.serialize()
        if not dict_source or dict_source == ["ALL"]:
            if include_auto_definitions or not serialized["is_auto_translation"]:
                ret.append(serialized)
        else:
            for source_id in serialized["source_ids"]:
                if source_id in dict_source:
                    ret.append(serialized)
                elif (
                    include_auto_definitions
                    and source_id.replace("🤖", "") in dict_source
                ):
                    ret.append(serialized)
    return ret


def serialize_lexical_entry(lexical_entry: _LexicalEntry) -> dict:
    return {
        "entry": lexical_entry.entry,
        "text": lexical_entry.text or "",
        "url": lexical_entry.url,
        "id": lexical_entry.id,
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


def get_emoji_for_cree_wordclass(
    word_class: Optional[str], animate_emoji: str = AnimateEmoji.default
) -> str:
    """
    Attempts to get an emoji description of the full wordclass.
    e.g., "👤👵🏽" for "nôhkom"
    """
    if word_class is None:
        return ""

    def to_fst_output_style(value):
        if value[0] == "N":
            return list(value.upper())
        elif value[0] == "V":
            return ["V", value[1:].upper()]
        else:
            return [value.title()]

    tags = to_fst_output_style(word_class)
    original = read_labels().emoji.get_longest(tags)

    ret = original
    if original:
        ret = use_preferred_animate_emoji(original, animate_emoji)
    return ret or ""


def use_preferred_animate_emoji(original: str, animate_emoji: str) -> str:
    return original.replace(
        emoji_for_value(AnimateEmoji.default), emoji_for_value(animate_emoji)
    )


def emoji_for_value(choice: str) -> str:
    if emoji := AnimateEmoji.choices.get(choice):
        return emoji
    return AnimateEmoji.choices[AnimateEmoji.default]


def get_lexical_info(
    result_analysis: Optional[RichAnalysis],
    animate_emoji: str,
    show_emoji: str,
    dict_source: list,
) -> List[dict]:
    if not result_analysis:
        return []

    result_analysis_tags = result_analysis.prefix_tags
    first_letters = extract_first_letters(result_analysis)

    lexical_info: List[_LexicalEntry] = []

    for i, tag in enumerate(result_analysis_tags):
        preverb_result: Optional[Preverb] = None
        reduplication_string: Optional[str] = None
        _type: Optional[LexicalEntryType] = None
        entry = None

        if tag in ["RdplW+", "RdplS+"]:
            reduplication_string = generate_reduplication_string(
                tag, first_letters[i + 1]
            )

        elif tag == "IC+":
            change_types = get_initial_change_types()
            _type = "Initial Change"
            entry = _InitialChangeResult(text=" ", definitions=change_types).serialize()

        elif tag.startswith("PV/"):
            preverb_text = tag.replace("PV/", "").replace("+", "")
            # Our FST analyzer doesn't return preverbs with diacritics
            # but we store variations of words in this table
            preverb_results = SourceLanguageKeyword.objects.filter(text=preverb_text)
            # get the actual wordform object and
            # make sure the result we return is an IPV
            if preverb_results:
                entries = []
                for preverb in preverb_results:
                    lexicon_result = Wordform.objects.get(id=preverb.wordform_id)
                    if lexicon_result:
                        _info = lexicon_result.linguist_info
                        if _info["wordclass"] == "IPV":
                            entry = serialize_wordform(
                                lexicon_result, animate_emoji, show_emoji, dict_source
                            )
                            if entry:
                                entries.append(entry)
                url = "search?q=" + preverb_text
                _type = "Preverb"
                try:
                    id: Optional[int] = entries[0]["id"]
                    result = _LexicalEntry(
                        entry=cast(Any, entries),
                        text=preverb_text,
                        url=url,
                        id=id,
                        type=_type,
                        original_tag=tag,
                    )
                    lexical_info.append(result)
                except IndexError:
                    # Pretend we didn't find it.
                    preverb_result1 = Wordform(text=preverb_text, is_lemma=True)
            else:
                # Can't find a match for the preverb in the database.
                # This happens when searching against the test database for
                # ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk, as the test database
                # lacks lacks ê and kî.
                preverb_result1 = Wordform(text=preverb_text, is_lemma=True)

        if reduplication_string is not None:
            entry = _ReduplicationResult(
                text=reduplication_string,
                definitions=[
                    {
                        "text": (
                            "Strong reduplication: intermittent, repeatedly, iteratively; again and again; here and there"
                            if tag == "RdplS+"
                            else "Weak Reduplication: ongoing, continuing"
                        )
                    }
                ],
            ).serialize()
            _type = "Reduplication"
        if entry and _type != "Preverb" and _type is not None:
            url = entry.get("lemma_url")
            id = None
            try:
                id = entry[0]["id"]
            except:
                id = None
            entry = [entry]
            result = _LexicalEntry(
                entry=entry,
                text=reduplication_string,
                url=url,
                id=id,
                type=_type,
                original_tag=tag,
            )
            lexical_info.append(result)
    return [serialize_lexical_entry(entry) for entry in lexical_info]


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
        if len(pieces) and len(pieces[-1]):
            return pieces[-1][0]
        else:
            return ""

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
    return [
        {
            "text": "\n".join(
                [
                    "a → ê",
                    "i → ê",
                    "o → wê",
                    "ê → iyê",
                    "â → iyâ",
                    "î → â / iyî",
                    "ô → iyô",
                ]
            )
        }
    ]


def to_list_of_fst_tags(raw_tags: Iterable[str]) -> list[FSTTag]:
    """
    Converts a series of tags (possibly from RichAnalysis or from splitting a smushed
    analysis) to a list of FSTTag. FSTTag instances can be used to looup relabellings!
    """
    return [FSTTag(t.strip("+")) for t in raw_tags]
