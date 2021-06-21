#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import readline
import sys
import typing
from argparse import ArgumentParser, BooleanOptionalAction
from functools import cache
from pathlib import Path
from typing import Iterable

import django
import foma

if typing.TYPE_CHECKING:
    # When this file is run directly as __main__, importing Django models at
    # top-level will blow up because Django is not configured yet.
    from morphodict.lexicon.models import Wordform

# Allow this script to be run directly from command line without pyproject.toml
# https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time
package_dir = os.fspath((Path(__file__).parent.parent).absolute())
if package_dir not in sys.path:
    sys.path.append(package_dir)


from CreeDictionary.phrase_translate.crk_tag_map import (
    noun_wordform_to_phrase,
    verb_wordform_to_phrase,
)

from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from CreeDictionary.utils.shared_res_dir import shared_fst_dir

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
        / "transcriptor-cw-eng-verb-entry2inflected-phrase-w-flags.fomabin"
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


def parse_analysis_and_tags(analysis):
    """Extract tags into a list in the form required by inflect_english_phrase

    >>> parse_analysis_and_tags('PV/e+PV/ki+atamihêw+V+TA+Cnj+1Pl+2SgO')
    ['PV/e+', 'PV/ki+', '+V', '+TA', '+Cnj', '+1Pl', '+2SgO']
    """
    head_tags, lemma, tail_tags = partition_analysis(analysis)
    return [t + "+" for t in head_tags] + ["+" + t for t in tail_tags]


def inflect_english_phrase(cree_wordform_tag_list_or_analysis, lemma_definition):
    if isinstance(cree_wordform_tag_list_or_analysis, list):
        cree_wordform_tag_list = cree_wordform_tag_list_or_analysis
    else:
        preverb_tags, lemma_, tags = partition_analysis(
            cree_wordform_tag_list_or_analysis
        )
        preverb_tags = [x + "+" for x in preverb_tags]
        tags = ["+" + x for x in tags]
        cree_wordform_tag_list = preverb_tags + tags

    if "+N" in cree_wordform_tag_list:
        tags_for_phrase = noun_wordform_to_phrase.map_tags(cree_wordform_tag_list)
        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        phrase = foma_lookup(eng_noun_entry_to_inflected_phrase_fst(), tagged_phrase)
        logger.debug("tagged_phrase = %s\n", tagged_phrase)
        return phrase.strip()

    elif "+V" in cree_wordform_tag_list:
        tags_for_phrase = verb_wordform_to_phrase.map_tags(cree_wordform_tag_list)
        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        phrase = foma_lookup(eng_verb_entry_to_inflected_phrase_fst(), tagged_phrase)
        logger.debug("tagged_phrase = %s\n", tagged_phrase)
        return phrase.strip()


def translate_and_print_wordforms(wordforms: Iterable[Wordform]):
    for wordform in wordforms:
        wordform_tags = parse_analysis_and_tags(wordform.analysis)
        print(f"wordform: {wordform.text} {wordform_tags}")

        lemma = wordform.lemma
        print(f"  lemma: {lemma.analysis}")

        for d in wordform.lemma.definitions.all():
            # Don’t try to re-translate already-translated items
            if [ds.abbrv for ds in d.citations.all()] == ["auto"]:
                continue

            print(f"    definition: {d} →")
            phrase = inflect_english_phrase(wordform_tags, d.text)
            if phrase is None:
                phrase = "(not supported)"
            print(f"      {phrase}")


def main():
    parser = ArgumentParser()
    parser.add_argument("--quiet", action=BooleanOptionalAction)
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ],
    )
    parser.add_argument("--django-settings-module", default="crkeng.site.settings")
    parser.add_argument("wordform", nargs="*")
    args = parser.parse_args()

    os.environ["DJANGO_SETTINGS_MODULE"] = args.django_settings_module
    django.setup()
    logger.setLevel(args.log_level)

    from morphodict.lexicon.models import Wordform

    def do_lookup(to_lookup: str):
        wordforms = Wordform.objects.filter(text=to_lookup)

        if wordforms.count() == 0:
            print("not found in database :/")
        else:
            translate_and_print_wordforms(wordforms)

    if args.wordform:
        for wordform in args.wordform:
            do_lookup(wordform)
        return

    if not args.quiet:
        print("Enter a Cree word to see English phrase translation")
        print("Some examples in the test database: acâhkosa, kimasinahikanisa")
    try:
        readline.read_init_file()
    except FileNotFoundError:
        # GNU readline can complain here, but libedit does not
        pass

    history_file = Path("~/.itwewina.translate.history").expanduser()
    try:
        if history_file.exists():
            readline.read_history_file(history_file)
        while True:
            try:
                to_lookup = input("> ")
                do_lookup(to_lookup)
            except EOFError:
                print("")
                break
    finally:
        # Not appending on every input because not supported by macOS python
        # using libedit aka editline
        readline.write_history_file(history_file)


if __name__ == "__main__":
    main()
