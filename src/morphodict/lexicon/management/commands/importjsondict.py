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
        for abbrv in ["CW", "MD", "AE", "ALD", "OS", "HD"]:
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

            fst_lemma = None
            if "fstLemma" in entry:
                fst_lemma = entry["fstLemma"]
            elif (analysis := entry.get("analysis")) is not None:
                fst_lemma = analysis[1]

            wf = Wordform.objects.create(
                text=entry["head"],
                raw_analysis=entry.get("analysis", None),
                fst_lemma=fst_lemma,
                paradigm=entry.get("paradigm", None),
                slug=validate_slug_format(entry["slug"]),
                is_lemma=True,
                linguist_info=entry.get("linguistInfo", {}),
            )
            wf.lemma = wf
            wf.save()

            should_instantiate_this_wordform = (
                (wf.analysis and wf.paradigm)
                if not settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT
                else (wf.fst_lemma and wf.paradigm)
            )

            # Instantiate wordforms
            if should_instantiate_this_wordform:
                lemma_text = (
                    wf.text
                    if not settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT
                    else wf.fst_lemma
                )
                for (
                    prefix_tags,
                    suffix_tags,
                ) in paradigm_manager.all_analysis_template_tags(wf.paradigm):
                    analysis = RichAnalysis((prefix_tags, lemma_text, suffix_tags))
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

            slug_base = wf.slug.split("@")[0]
            if wf.text != slug_base:
                SourceLanguageKeyword.objects.get_or_create(wordform=wf, text=slug_base)
            if wf.fst_lemma and wf.text != wf.fst_lemma:
                SourceLanguageKeyword.objects.get_or_create(
                    wordform=wf, text=wf.fst_lemma
                )
            if wf.raw_analysis is None:
                self.index_unanalyzed_form(wf)

            if "senses" not in entry:
                raise Exception(
                    f"Invalid importjson: no senses for lemma text={wf.text} slug={wf.slug}"
                )

            self.create_definitions(wf, entry["senses"])

            seen_slugs.add(wf.slug)

        for entry in form_definitions:
            try:
                lemma = Wordform.objects.get(slug=entry["formOf"])
            except Wordform.DoesNotExist:
                raise Exception(
                    f"Encountered wordform with formOf for unknown slug={entry['formOf']!r}"
                )

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

        if settings.MORPHODICT_SUPPORTS_AUTO_DEFINITIONS:
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
            TargetLanguageKeyword.objects.get_or_create(text=kw, wordform=wordform)

    def index_unanalyzed_form(self, wordform):
        """Index unanalyzed forms such as phrases, Cree preverbs

        These get put into the SourceLanguageKeyword table.
        """
        keywords = set(
            to_source_language_keyword(piece) for piece in wordform.text.split()
        )

        for kw in keywords:
            SourceLanguageKeyword.objects.get_or_create(text=kw, wordform=wordform)


def validate_slug_format(proposed_slug):
    """Raise an error if the proposed slug is invalid

    For example, if contains a slash."""

    # a regex would run faster, but getting the quoting right for a literal
    # backslash probably isn’t worth it
    FORBIDDEN_SLUG_CHARS = "/\\ "
    if any(c in FORBIDDEN_SLUG_CHARS for c in proposed_slug):
        raise Exception(
            f"{proposed_slug=!r} contains one of the forbidden slug chars {FORBIDDEN_SLUG_CHARS!r}"
        )

    return proposed_slug
