import json
import logging
from argparse import (
    ArgumentParser,
    RawDescriptionHelpFormatter,
)
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Iterable, Any

from django.core.management import BaseCommand
from django.db.models import Max, Q
from tqdm import tqdm

from CreeDictionary.phrase_translate.definition_processing import remove_parentheticals
from CreeDictionary.phrase_translate.translate import (
    inflect_english_phrase,
    FomaLookupNotFoundException,
    FomaLookupMultipleFoundException,
)
from morphodict.analysis.tag_map import UnknownTagError
from morphodict.lexicon.models import Wordform, Definition, DictionarySource

logger = logging.getLogger(__name__)


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

    def __str__(self):
        return "\n".join(f"{k}: {v:,}" for k, v in asdict(self).items())


def translate_single_definition(wordform, text, stats: TranslationStats):
    stats.wordforms_examined += 1

    assert wordform.analysis

    if any(
        t.startswith("PV/")
        ## This next commented-out line *is* useful, but it greatly increases
        ## the number of instantiated wordforms, like at least ~3x? It would be
        ## good to do some tests on whether that’s so many that it starts to
        ## slow things down before turning this on. Maybe it’ll be necessary to
        ## switch to computing them on-demand instead of pre-computing them all
        ## in advance?
        #
        # and t not in permitted_preverb_tags
        for t in wordform.analysis.prefix_tags
    ):
        logger.debug(
            f"skipping translation of preverb form {wordform.id} {wordform.text}"
        )
        stats.preverb_form += 1
        return

    try:
        input_text = remove_parentheticals(text)

        phrase = inflect_english_phrase(wordform.analysis, input_text)
    except UnknownTagError:
        raise Exception(f"Unknown tag for {wordform.text} {wordform.analysis}")
    except FomaLookupNotFoundException as e:
        logger.debug(f"Couldn’t handle {wordform.text}: {e}")
        stats.no_phrase_analysis_count += 1
        return None
    except FomaLookupMultipleFoundException as e:
        logger.debug(f"Couldn’t handle {wordform.text}: {e}")
        stats.multiple_phrase_analyses_count += 1
        return None

    if not phrase:
        logger.debug(f"no translation for {wordform.text} {wordform.analysis}")
        stats.no_translation_count += 1
        return None

    stats.definitions_created += 1
    return phrase


class Command(BaseCommand):
    help = """XXX No longer works

            This command no longer works. It required that all wordforms be
            instantiated in the database, even if they weren’t translatable, and
            running it multiple times could result in multiple copies of
            auto-definitions.
            
            Use importjsondict instead with the --translate-wordforms option
            instead.
        """

    def add_arguments(self, parser: ArgumentParser):
        pass

    def handle(self, *args, **options):
        raise NotImplementedError()
