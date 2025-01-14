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


logger = logging.getLogger(__name__)


def inflect_target_language_phrase(
    analysis: tuple | RichAnalysis, lemma_definition
) -> str | None:
    if isinstance(analysis, tuple):
        analysis = RichAnalysis(analysis)
    cree_wordform_tag_list = (
        analysis.prefix_tags
        + analysis.suffix_tags
        + settings.DEFAULT_TARGET_LANGUAGE_PHRASE_TAGS
    )

    if "+N" in cree_wordform_tag_list:
        tags_for_phrase = noun_wordform_to_phrase.map_tags(cree_wordform_tag_list)
        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        logger.debug("tagged_phrase = %s\n", tagged_phrase)
        phrase = inflect_target_noun_phrase(tagged_phrase)
        logger.debug("phrase = %s\n", phrase)
        return phrase.strip()

    elif "+V" in cree_wordform_tag_list:
        tags_for_phrase = verb_wordform_to_phrase.map_tags(cree_wordform_tag_list)
        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        logger.debug("tagged_phrase = %s\n", tagged_phrase)
        phrase = inflect_target_verb_phrase(tagged_phrase)
        logger.debug("phrase = %s\n", phrase)
        return phrase.strip()

    return None
