import json
import logging
from argparse import (
    ArgumentParser,
    BooleanOptionalAction,
    ArgumentDefaultsHelpFormatter,
)
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import transaction
from tqdm import tqdm

from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from CreeDictionary.utils.english_keyword_extraction import stem_keywords
from morphodict.analysis import RichAnalysis, strict_generator
from morphodict.lexicon import DEFAULT_IMPORTJSON_FILE
from morphodict.lexicon.models import (
    Wordform,
    Definition,
    DictionarySource,
    TargetLanguageKeyword,
    SourceLanguageKeyword,
)
from morphodict.lexicon.util import to_source_language_keyword

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Update the test database from an importjson file

    This command loads the dictionary data in an importjson file into the
    morphodict database. When run against an already-populated database, it
    synchronizes the database to match the contents of the importjson file.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        parser.add_argument(
            "--purge",
            action=BooleanOptionalAction,
            default=False,
            help="""
                Delete all existing entries that are not found in this import
                file. Used for importing a full dictionary file when keys may
                have changed.
            """,
        )
        parser.add_argument(
            "--atomic",
            action=BooleanOptionalAction,
            default=settings.DEBUG,
            help="""
                Run the import in a single transaction. This will make the
                import run much faster, but will lock up the database so that
                other processes can’t access it. Good for development use.
            """,
        )

        parser.add_argument(
            "json_file",
            help=f"The importjson file to import",
            nargs="?",
            default=DEFAULT_IMPORTJSON_FILE,
        )

    def handle(self, json_file, purge, atomic, **options):
        if atomic:
            with transaction.atomic():
                self.run_import(json_file=json_file, purge=purge)
        else:
            self.run_import(json_file=json_file, purge=purge)

    def run_import(self, json_file, purge):
        for abbrv in ["CW", "MD", "AE", "ALD", "OS"]:
            if not DictionarySource.objects.filter(abbrv=abbrv):
                DictionarySource.objects.create(abbrv=abbrv)

        paradigm_manager = default_paradigm_manager()

        # These slug collections track what should be purged
        existing_slugs = {
            v[0]
            for v in Wordform.objects.filter(slug__isnull=False).values_list("slug")
        }
        seen_slugs = set()

        form_definitions = []
        logger.info(f"Importing {json_file}")
        data = json.loads(Path(json_file).read_text())
        for entry in tqdm(data):
            if "formOf" in entry:
                form_definitions.append(entry)
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

            # Instantiate wordforms
            if wf.analysis and wf.paradigm:
                for (
                    prefix_tags,
                    suffix_tags,
                ) in paradigm_manager.all_analysis_template_tags(wf.paradigm):
                    analysis = RichAnalysis((prefix_tags, wf.text, suffix_tags))
                    for generated in strict_generator().lookup(analysis.smushed()):
                        # Skip re-instantiating lemma
                        if analysis == wf.analysis:
                            continue

                        Wordform.objects.create(
                            # For now, leaving paradigm and linguist_info empty;
                            # code can get that info from the lemma instead.
                            text=generated,
                            raw_analysis=analysis.tuple,
                            lemma=wf,
                            is_lemma=False,
                        )

            if wf.raw_analysis is None:
                self.index_unanalyzed_form(wf)

            self.create_definitions(wf, entry["senses"])

            seen_slugs.add(wf.slug)

        for entry in form_definitions:
            lemma = Wordform.objects.get(slug=entry["formOf"])

            wf, created = Wordform.objects.get_or_create(
                lemma=lemma, text=entry["head"], raw_analysis=entry["analysis"]
            )

            self.create_definitions(wf, entry["senses"])

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
        call_command("translatewordforms")

    def create_definitions(self, wordform, senses):
        keywords = set()

        for sense in senses:
            d = Definition.objects.create(
                wordform=wordform,
                text=sense["definition"],
            )
            for source in sense["sources"]:
                d.citations.add(source)

            keywords.update(stem_keywords(sense["definition"]))

        for kw in keywords:
            TargetLanguageKeyword.objects.create(text=kw, wordform=wordform)

    def index_unanalyzed_form(self, wordform):
        """Index unanalyzed forms such as phrases, Cree preverbs

        These get put into the SourceLanguageKeyword table.
        """
        keywords = set(
            to_source_language_keyword(piece) for piece in wordform.text.split()
        )

        for kw in keywords:
            SourceLanguageKeyword.objects.create(text=kw, wordform=wordform)
