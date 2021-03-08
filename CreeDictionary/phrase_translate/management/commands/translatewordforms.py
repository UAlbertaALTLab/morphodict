import logging
from argparse import ArgumentParser
from collections import defaultdict

from django.core.management import BaseCommand
from django.db.models import Max
from tqdm import tqdm

from API.models import Wordform, Definition, DictionarySource
from phrase_translate.translate import (
    inflect_english_phrase,
    parse_analysis_and_tags,
    FomaLookupException,
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


class Command(BaseCommand):
    help = """Translate wordforms into English phrases
    
    This command:
      - iterates over all wordforms in the database
      - uses the wordform inflection analysis and the phrase-translator FSTs to
        auto-generate phrase definitions from the definitions of the
        corresponding lemmas
      - saves these auto-generated wordform definitions to the database with
        source name “auto”
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--log-level")

    def handle(self, *args, **options):
        if options["log_level"]:
            logger.setLevel(options["log_level"])

        (ds, created_) = DictionarySource.objects.get_or_create(abbrv="auto")
        Definition.objects.filter(citations__abbrv="auto").delete()

        definitions = defaultdict(set)
        for d in Definition.objects.all().iterator():
            definitions[d.wordform_id].add(d)
        defn_count = sum(
            len(definition_list) for definition_list in definitions.values()
        )
        logger.info(f"loaded {defn_count} definitions")

        definition_buffer = InsertBuffer(manager=Definition.objects)
        citation_buffer = InsertBuffer(manager=Definition.citations.through.objects)

        # Some status counts to report at the end:
        # no translation returned, typically because no +N or +V tag
        no_translation = 0
        # foma returned n != 1 analyses
        error_count = 0

        wordform_count = Wordform.objects.count()
        for w in tqdm(
            Wordform.objects.select_related("lemma").iterator(), total=wordform_count
        ):
            for definition in definitions.get(w.lemma_id, []):
                try:
                    if not w.analysis:
                        continue

                    tags = parse_analysis_and_tags(w.analysis)
                    phrase = inflect_english_phrase(tags, definition.text)

                    if not phrase:
                        logger.debug(f"no translation for {w.text} {tags}")
                        no_translation += 1
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
                except KeyError as e:
                    logger.debug(
                        f"Unknown tag {e.args[0]} for {w.text} {w.analysis}", e
                    )
                    raise

                except FomaLookupException as e:
                    logger.debug(f"Couldn’t handle {w.text}: {e}")
                    error_count += 1

        definition_buffer.save()
        citation_buffer.save()
        print(f"Translation done. {no_translation=:,}, {error_count=:,}")
