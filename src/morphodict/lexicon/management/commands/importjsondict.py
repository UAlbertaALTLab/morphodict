import json
import logging
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

from django.core.management import BaseCommand, call_command
from django.db import transaction
from tqdm import tqdm

from CreeDictionary.utils.english_keyword_extraction import stem_keywords
from morphodict.lexicon.models import (
    Wordform,
    Definition,
    DictionarySource,
    TargetLanguageKeyword,
    SourceLanguageKeyword,
)
from morphodict.lexicon.util import strip_accents_for_search_lookups

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--purge",
            action=BooleanOptionalAction,
            # TODO: change default to False once working with full DBs
            default=True,
            help="""
                Delete all existing entries that are not found in this import
                file. Used for importing a full dictionary file when keys may
                have changed.
            """,
        )
        parser.add_argument("json_file")

    # atomic() is here only to speed things up at the moment; sqlite is ~5x
    # faster here when all the operations are inside of a transaction instead of
    # implicitly triggering a COMMIT after every db update.
    @transaction.atomic()
    def handle(self, json_file, purge, **options):
        for abbrv in ["CW", "MD", "AE", "ALD", "OS"]:
            if not DictionarySource.objects.filter(abbrv=abbrv):
                DictionarySource.objects.create(abbrv=abbrv)

        existing_slugs = {
            v[0]
            for v in Wordform.objects.filter(slug__isnull=False).values_list("slug")
        }
        seen_slugs = set()

        data = json.loads(Path(json_file).read_text())
        for entry in tqdm(data):
            if "formOf" in entry:
                logger.warning(f"Skipping non-lemma {entry['head']}")
                continue

            if existing := Wordform.objects.filter(slug=entry["slug"]).first():
                # Cascade should take care of all related objects.
                existing.delete()

            wf = Wordform.objects.create(
                text=entry["head"],
                raw_analysis=entry.get("analysis", None),
                paradigm=entry.get("paradigm", None),
                slug=entry["slug"],
                is_lemma=True,
                linguist_info=entry["linguistInfo"],
            )
            wf.lemma = wf
            wf.save()

            # Unanalyzed forms: phrases, Cree preverbs, &c.
            if wf.raw_analysis is None:
                variants = set()

                for piece in wf.text.split():
                    indexed_form = strip_accents_for_search_lookups(piece)
                    indexed_form = indexed_form.strip("-")
                    variants.add(indexed_form)

                for v in variants:
                    SourceLanguageKeyword.objects.create(text=v, wordform=wf)

            keywords = set()

            for sense in entry["senses"]:
                d = Definition.objects.create(
                    wordform=wf,
                    text=sense["definition"],
                )
                for source in sense["sources"]:
                    try:
                        d.citations.add(source)
                    except:
                        breakpoint()
                        raise

                keywords.update(stem_keywords(sense["definition"]))

            for kw in keywords:
                TargetLanguageKeyword.objects.create(text=kw, wordform=wf)

            seen_slugs.add(wf.slug)

        if purge:
            rows, breakdown = Wordform.objects.filter(
                slug__in=existing_slugs - seen_slugs
            ).delete()
            if rows:
                logger.warning(
                    f"Purged {rows:,} rows from database for existing entries not found in import file: %r",
                    breakdown,
                )
        call_command("builddefinitionvectors")
