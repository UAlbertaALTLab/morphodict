import logging
import re
from argparse import ArgumentParser

from django.core.management import BaseCommand
from django.db.models import Max
from tqdm import tqdm

import foma

import phrase_translate
from API.models import Wordform, Definition, DictionarySource
from phrase_translate.translate import (
    inflect_english_phrase,
    parse_analysis_and_tags,
    FomaLookupException,
)
from utils import shared_res_dir

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Please fill me in.
    
    Otherwise nobody will know what this command does.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--log-level")

    def handle(self, *args, **options):
        if options["log_level"]:
            logger.setLevel(options["log_level"])

        (ds, created_) = DictionarySource.objects.get_or_create(abbrv="auto")
        Definition.objects.filter(citations__abbrv="auto").delete()

        definitions = {d.wordform_id: d for d in Definition.objects.all()}
        logger.info(f"Loaded {len(definitions):,} definitions")

        wordform_count = Wordform.objects.count()

        for w in tqdm(
            Wordform.objects.all().select_related("lemma").iterator(),
            total=wordform_count,
        ):
            # Note we see as many as four definitions for a word from Arok
            wordform_definition1 = definitions.get(w.lemma_id, None)
            if wordform_definition1 is None:
                logger.info(f"No definition found for lemma of {w}")
            else:
                try:
                    tags = parse_analysis_and_tags(w.analysis)
                    phrase = inflect_english_phrase(tags, wordform_definition1.text)

                    if not phrase:
                        logger.warning(f"no translation for {w.text} {tags}")
                        continue

                    max_id = Definition.objects.aggregate(Max("id"))
                    if max_id["id__max"] is None:
                        id = 0
                    else:
                        id = max_id["id__max"] + 1

                    d = Definition.objects.create(id=id, text=phrase, wordform_id=w.id)
                    d.citations.add(ds)
                    d.save()
                    logger.info(f"saved definition {d.id} {w.text}: {d}")
                except KeyError as e:
                    logger.error(f"Unknown tag for {w.text} {w.analysis}", e)
                    raise

                except FomaLookupException as e:
                    logger.warning(f"Couldn’t handle {w.text}: {e}")
