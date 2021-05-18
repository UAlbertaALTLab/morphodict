import json
import logging
from argparse import (
    ArgumentParser,
    RawDescriptionHelpFormatter,
)
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Iterable

from django.core.management import BaseCommand
from django.db.models import Max, Q, prefetch_related_objects
from tqdm import tqdm

from CreeDictionary.API.models import Wordform, Definition, DictionarySource
from CreeDictionary.phrase_translate.definition_processing import remove_parentheticals
from CreeDictionary.phrase_translate.tag_map import UnknownTagError
from CreeDictionary.phrase_translate.translate import (
    inflect_english_phrase,
    parse_analysis_and_tags,
    FomaLookupNotFoundException,
    FomaLookupMultipleFoundException,
)

logger = logging.getLogger(__name__)


class InsertBuffer:
    """A container for objects to be bulk-inserted.

    Will automatically assign IDs to provided objects, and call
    `manager.bulk_create` every `count` objects. The caller is responsible for
    calling `save()` one final time when done.
    """

    def __init__(self, manager, count=500):
        self._queryset = manager
        self._count = count
        self._buffer = []

        # This bit is cargo-culted from elsewhere in this project, where it is
        # indicated that auto-increment IDs do not work with bulk_create,
        # requiring the use of
        #
        #     id = models.PositiveIntegerField(primary_key=True)
        #
        # This is a claim I have not verified. Maybe that’s only to make it more
        # convenient to bulk-create objects that reference each other as foreign
        # keys?
        max_id = manager.aggregate(Max("id"))["id__max"]
        if max_id is None:
            max_id = 0
        self._next_id = max_id + 1

    def add(self, obj):
        if obj.id is None:
            obj.id = self._next_id
            self._next_id += 1
        self._buffer.append(obj)

        if len(self._buffer) >= self._count:
            self.save()

    def save(self):
        self._queryset.bulk_create(self._buffer)
        self._buffer = []


@dataclass
class TranslationStats:
    wordforms_examined: int = 0
    # wordforms without an analysis
    no_wordform_analysis: int = 0
    definitions_created: int = 0
    # no translation returned, typically because no +N or +V tag
    no_translation_count: int = 0
    # phrase generator FST returned 0 analyses
    no_phrase_analysis_count: int = 0
    # phrase generator FST returned multiple analyses
    multiple_phrase_analyses_count: int = 0

    def __str__(self):
        return "\n".join(f"{k}: {v:,}" for k, v in asdict(self).items())


class Command(BaseCommand):
    help = """Translate wordforms into English phrases
    
    This command:
      - iterates over wordforms, by default everything in the database
      - uses the wordform inflection analysis and the phrase-translator FSTs to
        auto-generate phrase definitions from the definitions of the
        corresponding lemmas
      - saves these auto-generated wordform definitions to the database with
        source name “auto”
    """

    def add_arguments(self, parser: ArgumentParser):
        # Retain markdown-ish formatting in command help
        parser.formatter_class = RawDescriptionHelpFormatter

        # Prevent our args from getting all mixed in with default Django ones
        group = parser.add_argument_group("translatewordforms-specific options")
        group.add_argument(
            "--jsonl-only",
            help="""
            Instead of writing to the database, write translations to the named
            JSONL file instead. Useful for further review or analysis.
            """,
        )
        group.add_argument("--log-level")
        group.add_argument(
            "--wordforms",
            nargs="+",
            help="""
            Only translate the given wordforms, instead of the default of
            processing the entire database
            """,
        )

    def generate_translations(self) -> Iterable[tuple[Wordform, list[Definition]]]:
        logger.info("Building cache of existing non-auto definitions")
        definitions = defaultdict(set)
        for d in Definition.objects.filter(
            ~Q(citations__abbrv="auto")
        ).prefetch_related("citations"):
            definitions[d.wordform_id].add(d)
        defn_count = sum(
            len(definition_list) for definition_list in definitions.values()
        )
        logger.info(f"Loaded {defn_count} definitions")

        wordform_count = self.wordforms_queryset.count()
        for wordform in tqdm(self.wordforms_queryset.iterator(), total=wordform_count):
            self.translation_stats.wordforms_examined += 1

            wordform_auto_definitions: list[Definition] = []

            if not wordform.analysis:
                logger.debug(f"no analysis for {wordform.id} {wordform.text}")
                self.translation_stats.no_wordform_analysis += 1
                continue

            for definition in definitions.get(wordform.lemma_id, []):
                tags = parse_analysis_and_tags(wordform.analysis)
                try:
                    input_text = remove_parentheticals(definition.text)

                    phrase = inflect_english_phrase(tags, input_text)
                except UnknownTagError:
                    raise Exception(
                        f"Unknown tag for {wordform.text} {wordform.analysis}"
                    )
                except FomaLookupNotFoundException as e:
                    logger.debug(f"Couldn’t handle {wordform.text}: {e}")
                    self.translation_stats.no_phrase_analysis_count += 1
                    continue
                except FomaLookupMultipleFoundException as e:
                    logger.debug(f"Couldn’t handle {wordform.text}: {e}")
                    self.translation_stats.multiple_phrase_analyses_count += 1
                    continue

                if not phrase:
                    logger.debug(f"no translation for {wordform.text} {tags}")
                    self.translation_stats.no_translation_count += 1
                    continue

                wordform_auto_definitions.append(
                    Definition(
                        text=phrase,
                        wordform_id=wordform.id,
                        auto_translation_source=definition,
                    )
                )

                self.translation_stats.definitions_created += 1

            yield wordform, wordform_auto_definitions

    def write_translations_to_database(self, wordforms) -> None:
        if wordforms:
            wordform_filter = dict(wordform__in=self.wordforms_queryset)
        else:
            wordform_filter = {}  # No restriction

        logger.info("Removing existing auto-definitions")
        deleted_rows, deleted_row_details = Definition.objects.filter(
            citations__abbrv="auto", **wordform_filter
        ).delete()
        logger.info(
            f"Deleted {deleted_rows:,} rows for auto-definitions: {deleted_row_details}"
        )

        (ds, created_) = DictionarySource.objects.get_or_create(abbrv="auto")

        definition_buffer = InsertBuffer(manager=Definition.objects)
        citation_buffer = InsertBuffer(manager=Definition.citations.through.objects)

        for _, definitions in self.generate_translations():
            for auto_definition in definitions:
                definition_buffer.add(auto_definition)
                citation_buffer.add(
                    Definition.citations.through(
                        dictionarysource_id=ds.abbrv,
                        definition_id=auto_definition.id,
                    )
                )

        definition_buffer.save()
        citation_buffer.save()
        logger.info("Translation done")

    def write_translations_to_jsonl(self, filename):
        with open(filename, "w") as out:
            for wordform, auto_definitions in self.generate_translations():
                out.write(
                    json.dumps(
                        {
                            "wordform_text": wordform.text,
                            "wordform_analysis": wordform.analysis,
                            "wordform_lemma_text": wordform.lemma.text,
                            "wordform_lemma_analysis": wordform.lemma.analysis,
                            "translations": [
                                (
                                    d.auto_translation_source.text,
                                    ",".join(
                                        c.abbrv
                                        for c in d.auto_translation_source.citations.all()
                                    ),
                                    d.text,
                                )
                                for d in auto_definitions
                            ],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    def handle(self, *args, **options):
        if options["log_level"]:
            logger.parent.setLevel(options["log_level"])

        extra_kwargs = {}
        if options["wordforms"]:
            extra_kwargs = dict(text__in=options["wordforms"])
        self.wordforms_queryset = Wordform.objects.filter(
            is_lemma=False, **extra_kwargs
        )

        self.translation_stats = TranslationStats()

        try:
            if filename := options["jsonl_only"]:
                self.write_translations_to_jsonl(filename)
            else:
                self.write_translations_to_database(wordforms=options["wordforms"])

        finally:
            logger.info("Stats:")
            logger.info(self.translation_stats)
