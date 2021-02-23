#!/usr/bin/env python3

import logging
import os
import re
import readline
from argparse import ArgumentParser, BooleanOptionalAction
from functools import cache
from pathlib import Path

import django
import foma

from phrase_translate.tag_map import (
    noun_wordform_to_phrase_tag_info,
    verb_wordform_to_phrase_tag_info,
)
from utils.fst_analysis_parser import partition_analysis
from utils.shared_res_dir import shared_fst_dir

logger = logging.getLogger(__name__)


noun_wordform_to_phrase_tags = {}
noun_tag_precedences = {}
for k, v, prec in noun_wordform_to_phrase_tag_info:
    if v == "copy":
        v = k[1:] + "+"
    noun_wordform_to_phrase_tags[k] = v

    if v is not None:
        noun_tag_precedences[v] = prec

verb_wordform_to_phrase_tags = {}
verb_tag_precedences = {}
for k, v, prec in verb_wordform_to_phrase_tag_info:
    if v == "copy":
        v = k[1:] + "+"
    verb_wordform_to_phrase_tags[k] = v

    if v is not None:
        verb_tag_precedences[v] = prec


@cache
def creeRelaxedAnalyzerFst():
    return foma.FST.load(shared_fst_dir / "crk-anl-desc-dict.fomabin")


@cache
def englishNounEntryToInflectedPhraseFst():
    return foma.FST.load(
        shared_fst_dir
        / "transcriptor-cw-eng-noun-entry2inflected-phrase-w-flags.fomabin"
    )


@cache
def englishVerbEntryToInflectedPhraseFst():
    return foma.FST.load(
        shared_fst_dir / "transcriptor-cw-eng-verb-entry2inflected-phrase.fomabin"
    )


class FomaLookupException(Exception):
    pass


def _foma_wrapper(fst, func, thing_to_lookup):
    l = list(func(fst, thing_to_lookup))
    if len(l) == 0:
        raise FomaLookupException(f"{thing_to_lookup} not found")
    if len(l) > 1:
        raise FomaLookupException(f"multiple found for {thing_to_lookup}: {l}")
    return l[0]


def foma_up_wrapper(fst, thing_to_lookup):
    return _foma_wrapper(fst, foma.FST.apply_up, thing_to_lookup)


def foma_down_wrapper(fst, thing_to_lookup):
    return _foma_wrapper(fst, foma.FST.apply_down, thing_to_lookup)


tag_re = re.compile(
    r"""
    ^
    \s* # optional space
    ([^+]*) # the lemma: not tags
    ( # then a group of:
        ( # tags:
            \+ # literal +
             [^+]+ # at least one non-‘+’ character
        )* # zero or more of them
    )
    $
""",
    re.VERBOSE,
)


def parse_analysis_and_tags(analysis):
    """ fill me in """
    analysis_and_tags = tag_re.match(analysis)
    if not analysis_and_tags:
        raise Exception("could not parse analysis")

    lemma = analysis_and_tags.group(1)
    logger.debug(f"{lemma=}")
    tags = analysis_and_tags.group(2)
    wordform_tag_list = list("+" + tag for tag in tags.split("+") if tag)
    logger.debug(f"{wordform_tag_list=}")
    return wordform_tag_list


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
        tags_for_phrase = []

        for wordform_tag in cree_wordform_tag_list:
            phrase_tag = noun_wordform_to_phrase_tags[wordform_tag]
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        logger.debug(f"{tags_for_phrase=}")

        tags_for_phrase.sort(key=lambda tag: noun_tag_precedences[tag])

        logger.debug(f"{tags_for_phrase=}")

        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        logger.debug(f"{tagged_phrase=}")
        phrase = foma_down_wrapper(
            englishNounEntryToInflectedPhraseFst(), tagged_phrase
        )

        return phrase.strip()

    if "+V" in cree_wordform_tag_list:
        tags_for_phrase = []

        for wordform_tag in cree_wordform_tag_list:
            phrase_tag = verb_wordform_to_phrase_tags[wordform_tag]
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        logger.debug(f"{tags_for_phrase=}")

        tags_for_phrase.sort(key=lambda tag: verb_tag_precedences[tag])

        logger.debug(f"{tags_for_phrase=}")

        tagged_phrase = f"{''.join(tags_for_phrase)} {lemma_definition}"
        logger.debug(f"{tagged_phrase=}")
        phrase = foma_down_wrapper(
            englishVerbEntryToInflectedPhraseFst(), tagged_phrase
        )

        return phrase


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
    parser.add_argument("--django-settings-module", default="CreeDictionary.settings")
    parser.add_argument("wordform", nargs="*")
    args = parser.parse_args()

    os.environ["LOG_LEVEL"] = args.log_level
    os.environ["DJANGO_SETTINGS_MODULE"] = args.django_settings_module
    django.setup()

    from API.models import Wordform

    def do_lookup(to_lookup: str):
        wordforms = Wordform.objects.filter(text=to_lookup).select_related("lemma")

        for wordform in wordforms:
            wordform_tags = parse_analysis_and_tags(wordform.analysis)
            print(f"wordform: {wordform.text} {wordform_tags}")

            lemma = wordform.lemma
            print(f"  lemma: {lemma.analysis}")

            for d in wordform.lemma.definitions.all():
                print(f"    definition: {d} →")
                phrase = inflect_english_phrase(wordform_tags, d.text)
                if phrase is None:
                    phrase = "(not supported)"
                print(f"      {phrase}")

        if wordforms.count() == 0:
            print("not found in database :/")

    if args.wordform:
        for wordform in args.wordform:
            do_lookup(wordform)
        return

    if not args.quiet:
        print("Enter a Cree word to see English phrase translation")
        print("Some examples in the test database: acâhkosa, kimasinahikanisa")
    try:
        readline.read_init_file()
        history_file = Path("~/.itwewina.translate.history").expanduser()
        if history_file.exists():
            readline.read_history_file(history_file)
        while True:
            to_lookup = input("> ")
            do_lookup(to_lookup)
    except EOFError:
        print("")
        pass
    finally:
        # Not appending on every input because not supported by macOS python
        # using libedit aka editline
        readline.write_history_file(history_file)


if __name__ == "__main__":
    main()
