from hfst_altlab import TransducerFile
from functools import cache

from morphodict.utils.shared_res_dir import shared_fst_dir


@cache
def eng_noun_entry_to_inflected_phrase_fst():
    return TransducerFile(
        shared_fst_dir
        / "transcriptor-cw-eng-noun-entry2inflected-phrase-w-flags.fomabin"
    )


@cache
def eng_verb_entry_to_inflected_phrase_fst():
    return TransducerFile(
        shared_fst_dir
        / "transcriptor-cw-eng-verb-entry2inflected-phrase-w-flags-and-templates.fomabin"
    )


@cache
def eng_phrase_to_crk_features_fst():
    return TransducerFile(
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


def foma_lookup(fst:TransducerFile, thing_to_lookup:str) -> str:
    # Updated from FOMA lookup - currently using an HFST lookup instead,
    # This reduces dependencies and allows for migration to python 3.14.

    l = fst.lookup(thing_to_lookup)

    if len(l) == 0:
        raise FomaLookupNotFoundException(thing_to_lookup)
    if len(l) > 1:
        raise FomaLookupMultipleFoundException(thing_to_lookup, l)
    return l[0]


def inflect_target_noun_phrase(
    tags_for_phrase: list[str], lemma_definition: str
) -> str:
    tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"

    return foma_lookup(eng_noun_entry_to_inflected_phrase_fst(), tagged_phrase)


def inflect_target_verb_phrase(
    tags_for_phrase: list[str], lemma_definition: str
) -> str:
    tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"

    return foma_lookup(eng_verb_entry_to_inflected_phrase_fst(), tagged_phrase)


def source_phrase_analyses(query: str) -> list[str]:
    return [r for r in eng_phrase_to_crk_features_fst().lookup(query)]


def fst_analyses(text):
    def decode_foma_results(fst: TransducerFile, query: str):
        return [r for r in fst.lookup(query)]

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
