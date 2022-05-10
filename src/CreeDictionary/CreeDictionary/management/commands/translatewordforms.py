import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand
from django.db.models import Max
from tqdm import tqdm

from CreeDictionary.phrase_translate.translate import inflect_english_phrase, FomaLookupException
from morphodict.lexicon.models import DictionarySource, Definition, Wordform

logger = logging.getLogger(__name__)


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
                    if not w.analysis:
                        continue
                    phrase = inflect_english_phrase(w.analysis, wordform_definition1.text)

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
                    logger.error(
                        f"Unknown tag {e.args[0]} for {w.text} {w.analysis}", e
                    )
                    raise

                except FomaLookupException as e:
                    logger.warning(f"Couldn’t handle {w.text}: {e}")
