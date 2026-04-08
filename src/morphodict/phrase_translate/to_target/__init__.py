import logging
from django.conf import settings
from morphodict.analysis import RichAnalysis
from morphodict.phrase_translate.source_tag_map import (
    noun_wordform_to_phrase,
    verb_wordform_to_phrase,
)
from morphodict.phrase_translate.fst import (
    inflect_target_noun_phrase,
    inflect_target_verb_phrase,
)
from morphodict.phrase_translate.tpt import tsuutina_inflect_target_phrase

logger = logging.getLogger(__name__)


def inflect_target_language_phrase(
    analysis: tuple | RichAnalysis,
    lemma_definition,
    use_fst: bool = settings.USE_FST_PHRASE_TRANSLATE,
    extra_args: dict = {},
) -> str | None:
    if isinstance(analysis, tuple):
        analysis = RichAnalysis(analysis)
    wordform_tag_list = (
        analysis.prefix_tags
        + analysis.suffix_tags
        + settings.DEFAULT_TARGET_LANGUAGE_PHRASE_TAGS
    )

    if not use_fst:
        phrase = tsuutina_inflect_target_phrase(
            wordform_tag_list, lemma_definition, extra_args
        )
        return phrase.strip()

    if "+N" in wordform_tag_list:
        tags_for_phrase = noun_wordform_to_phrase.map_tags(wordform_tag_list)
        phrase = inflect_target_noun_phrase(tags_for_phrase, lemma_definition)
        return phrase.strip()

    elif "+V" in wordform_tag_list:
        tags_for_phrase = verb_wordform_to_phrase.map_tags(wordform_tag_list)
        phrase = inflect_target_verb_phrase(tags_for_phrase, lemma_definition)
        return phrase.strip()

    return None
