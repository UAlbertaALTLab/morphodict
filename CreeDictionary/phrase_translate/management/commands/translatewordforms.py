import logging
from argparse import (
    ArgumentParser,
    RawDescriptionHelpFormatter,
)
from collections import defaultdict
from dataclasses import dataclass, asdict

from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Max, Q
from tqdm import tqdm

from API.models import Wordform, Definition, DictionarySource
from phrase_translate.tag_map import UnknownTagError
from phrase_translate.translate import (
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
class InsertStats:
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
        group.add_argument("--log-level")
        group.add_argument(
            "--wordforms",
            nargs="+",
            help="""
            Only translate the given wordforms, instead of the default of
            processing the entire database
            """,
        )

    def handle(self, *args, **options):
        if options["log_level"]:
            logger.parent.setLevel(options["log_level"])

        (ds, created_) = DictionarySource.objects.get_or_create(abbrv="auto")

        extra_kwargs = {}
        if options["wordforms"]:
            extra_kwargs = dict(text__in=options["wordforms"])
        wordforms_queryset = Wordform.objects.filter(is_lemma=False, **extra_kwargs)

        logger.info("Removing existing auto-definitions")
        if options["wordforms"]:
            wordform_filter = dict(wordform__in=wordforms_queryset)
        else:
            wordform_filter = {}
        deleted_rows, deleted_row_details = Definition.objects.filter(
            citations__abbrv="auto", **wordform_filter
        ).delete()
        logger.info(
            f"Deleted {deleted_rows:,} rows for auto-definitions: {deleted_row_details}"
        )

        logger.info("Building cache of existing non-auto definitions")
        definitions = defaultdict(set)
        for d in Definition.objects.filter(~Q(citations__abbrv="auto")).iterator():
            definitions[d.wordform_id].add(d)
        defn_count = sum(
            len(definition_list) for definition_list in definitions.values()
        )
        logger.info(f"Loaded {defn_count} definitions")

        definition_buffer = InsertBuffer(manager=Definition.objects)
        citation_buffer = InsertBuffer(manager=Definition.citations.through.objects)

        insert_stats = InsertStats()

        try:
            wordform_count = wordforms_queryset.count()
            for w in tqdm(wordforms_queryset.iterator(), total=wordform_count):
                insert_stats.wordforms_examined += 1

                if not w.analysis:
                    logger.debug(f"no analysis for {w.id} {w.text}")
                    insert_stats.no_wordform_analysis += 1
                    continue

                for definition in definitions.get(w.lemma_id, []):
                    tags = parse_analysis_and_tags(w.analysis)
                    try:
                        phrase = inflect_english_phrase(tags, definition.text)
                    except UnknownTagError:
                        raise Exception(f"Unknown tag for {w.text} {w.analysis}")
                    except FomaLookupNotFoundException as e:
                        logger.debug(f"Couldn’t handle {w.text}: {e}")
                        insert_stats.no_phrase_analysis_count += 1
                        continue
                    except FomaLookupMultipleFoundException as e:
                        logger.debug(f"Couldn’t handle {w.text}: {e}")
                        insert_stats.multiple_phrase_analyses_count += 1
                        continue

                    if not phrase:
                        logger.debug(f"no translation for {w.text} {tags}")
                        insert_stats.no_translation_count += 1
                        continue

                    auto_definition = Definition(
                        text=phrase,
                        wordform_id=w.id,
                        auto_translation_source_id=definition.id,
                    )

                    definition_buffer.add(auto_definition)
                    citation_buffer.add(
                        Definition.citations.through(
                            dictionarysource_id=ds.abbrv,
                            definition_id=auto_definition.id,
                        )
                    )
                    insert_stats.definitions_created += 1

            definition_buffer.save()
            citation_buffer.save()
            logger.info("Translation done")
        finally:
            logger.info("Stats:")
            logger.info(insert_stats)
