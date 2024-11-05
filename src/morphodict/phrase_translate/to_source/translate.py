#!/usr/bin/env python3

from __future__ import annotations

import logging
import os
import readline
import sys
import typing
from argparse import (
    ArgumentParser,
)
from argparse import BooleanOptionalAction
from collections import Counter
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable

import django

from morphodict.phrase_translate.definition_cleanup import cleanup_target_definition_for_translation
from morphodict.phrase_translate.fst import inflect_english_phrase, FomaLookupNotFoundException, FomaLookupMultipleFoundException
from morphodict.analysis.tag_map import UnknownTagError

if typing.TYPE_CHECKING:
    # When this file is run directly as __main__, importing Django models at
    # top-level will blow up because Django is not configured yet.
    from morphodict.lexicon.models import Wordform

# Allow this script to be run directly from command line without pyproject.toml
# https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time
package_dir = os.fspath((Path(__file__).parent.parent).absolute())
if package_dir not in sys.path:
    sys.path.append(package_dir)


logger = logging.getLogger(__name__)


def translate_and_print_wordforms(wordforms: Iterable[Wordform]):
    for wordform in wordforms:
        print(f"wordform: {wordform.text} {wordform.analysis}")

        lemma = wordform.lemma

        if lemma is None:
            continue

        print(f"  lemma: {lemma.analysis}")

        for d in lemma.definitions.all():
            # Don’t try to re-translate already-translated items
            if d.auto_translation_source_id is not None:
                continue

            print(f"    definition: {d} →")
            phrase = inflect_english_phrase(wordform.analysis, d.core_definition)
            if phrase is None:
                phrase = "(not supported)"
            print(f"      {phrase}")


@dataclass
class TranslationStats:
    wordforms_examined: int = 0
    definitions_created: int = 0
    # no translation returned, typically because no +N or +V tag
    no_translation_count: int = 0
    # phrase generator FST returned 0 analyses
    no_phrase_analysis_count: int = 0
    # phrase generator FST returned multiple analyses
    multiple_phrase_analyses_count: int = 0
    # analysis contains preverb tags, which we don’t have mappings for
    preverb_form: int = 0
    # How often are we seeing various unknown tags?
    unknown_tags_during_auto_translation: Counter = field(default_factory=Counter)

    def __str__(self):
        ret = []

        for field_name, value in asdict(self).items():
            if isinstance(value, int):
                formatted = format(value, ",")
            elif isinstance(value, Counter):
                # asdict messes up Counter objects
                value = getattr(self, field_name)

                formatted = ", ".join(
                    f"{count:,}x {item}" for item, count in value.most_common()
                )
            else:
                formatted = str(value)
            ret.append(f"{field_name}: {formatted}")

        return "\n".join(ret)


def translate_single_definition(inflected_wordform, lemma_definition, stats: TranslationStats):
    stats.wordforms_examined += 1

    assert inflected_wordform.analysis

    # if any(
    #     t.startswith("PV/")
    #     ## This next commented-out line *is* useful, but it greatly increases
    #     ## the number of instantiated wordforms, like at least ~3x? It would be
    #     ## good to do some tests on whether that’s so many that it starts to
    #     ## slow things down before turning this on. Maybe it’ll be necessary to
    #     ## switch to computing them on-demand instead of pre-computing them all
    #     ## in advance?
    #     #
    #     # and t not in permitted_preverb_tags
    #     for t in wordform.analysis.prefix_tags
    # ):
    #     logger.debug(
    #         f"skipping translation of preverb form {wordform.id} {wordform.text}"
    #     )
    #     stats.preverb_form += 1
    #     return

    try:
        input_text = cleanup_target_definition_for_translation(lemma_definition)

        phrase = inflect_english_phrase(inflected_wordform.analysis, input_text)
    except UnknownTagError as e:
        logger.debug(f"Unknown tag in {inflected_wordform.text} {inflected_wordform.analysis}: {e}")
        stats.unknown_tags_during_auto_translation[e.args[0]] += 1
        return None
    except FomaLookupNotFoundException as e:
        logger.debug(f"Couldn’t handle {inflected_wordform.text}: {e}")
        stats.no_phrase_analysis_count += 1
        return None
    except FomaLookupMultipleFoundException as e:
        logger.debug(f"Couldn’t handle {inflected_wordform.text}: {e}")
        stats.multiple_phrase_analyses_count += 1
        return None

    if not phrase:
        logger.debug(f"no translation for {inflected_wordform.text} {inflected_wordform.analysis}")
        stats.no_translation_count += 1
        return None

    stats.definitions_created += 1
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
