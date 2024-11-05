import foma
from functools import cache
import logging

from morphodict.utils.shared_res_dir import shared_fst_dir
from morphodict.analysis import RichAnalysis
from morphodict.phrase_translate.source_tag_map import (
    noun_wordform_to_phrase,
    verb_wordform_to_phrase,
)

logger = logging.getLogger(__name__)

@cache
def eng_noun_entry_to_inflected_phrase_fst():
    return foma.FST.load(
        shared_fst_dir
        / "transcriptor-cw-eng-noun-entry2inflected-phrase-w-flags.fomabin"
    )


@cache
def eng_verb_entry_to_inflected_phrase_fst():
    return foma.FST.load(
        shared_fst_dir
        / "transcriptor-cw-eng-verb-entry2inflected-phrase-w-flags-and-templates.fomabin"
    )


@cache
def eng_phrase_to_crk_features_fst():
    return foma.FST.load(
        shared_fst_dir / "transcriptor-eng-phrase2crk-features.fomabin"
    )


class FomaLookupException(Exception):
    pass


class FomaLookupNotFoundException(FomaLookupException):
    def __init__(self, thing_to_lookup):
        super().__init__(f"{thing_to_lookup!r} not found in FST")


class FomaLookupMultipleFoundException(FomaLookupException):
    def __init__(self, thing_to_lookup, result_list):
        super().__init__(
            f"{len(result_list)} things were returned, but only 1 was expected for {thing_to_lookup!r}: {result_list!r}"
        )


def foma_lookup(fst, thing_to_lookup):
    # Caution: Python `foma.FST.apply_up` and `foma.FST.apply_down` do not cache
    # the FST object built by the C-language `apply_init()` function in libfoma,
    # so they are about 100x slower than calling the C-language `apply_up` and
    # `apply_down` directly.
    #
    # But __getitem__ does do the caching and runs at an acceptable speed.
    l = fst[thing_to_lookup]
    if len(l) == 0:
        raise FomaLookupNotFoundException(thing_to_lookup)
    if len(l) > 1:
        raise FomaLookupMultipleFoundException(thing_to_lookup, l)
    return l[0].decode("UTF-8")

def inflect_target_noun_phrase(tagged_phrase):
    return foma_lookup(eng_noun_entry_to_inflected_phrase_fst(), tagged_phrase)

def inflect_target_verb_phrase(tagged_phrase):
    return foma_lookup(eng_verb_entry_to_inflected_phrase_fst(), tagged_phrase)

def source_phrase_analyses(query):
    return [
        r.decode("UTF-8") for r in eng_phrase_to_crk_features_fst()[query]
    ]

def inflect_english_phrase(analysis, lemma_definition):
    if isinstance(analysis, tuple):
        analysis = RichAnalysis(analysis)
    cree_wordform_tag_list = analysis.prefix_tags + analysis.suffix_tags

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


def fst_analyses(text):
    def decode_foma_results(fst, query):
        return [r.decode("UTF-8") for r in fst[query]]
    
    return {
            "eng_noun_entry2inflected-phrase": decode_foma_results(
                eng_noun_entry_to_inflected_phrase_fst(), text
            ),
            "eng_verb_entry2inflected-phrase": decode_foma_results(
                eng_verb_entry_to_inflected_phrase_fst(), text
            ),
            "eng_phrase_to_crk_features": decode_foma_results(
                eng_phrase_to_crk_features_fst(), text
            ),
    }