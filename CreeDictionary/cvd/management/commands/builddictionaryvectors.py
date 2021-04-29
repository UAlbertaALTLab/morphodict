import logging
from argparse import ArgumentParser
from os import fspath

from django.core.management import BaseCommand
from gensim.models import KeyedVectors
from tqdm import tqdm

from API.models import Definition
from cvd import (
    shared_vector_model_dir,
    google_news_vectors,
    extract_keyed_words,
    vector_for_keys,
)
from cvd.definition_keys import definition_to_cvd_key

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Create a vector model from current definitions"""

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--output-file", default=shared_vector_model_dir / "definitions.kv"
        )

    def handle(self, *args, **options):
        definitions = Definition.objects.filter(
            auto_translation_source_id__isnull=True
        ).prefetch_related("wordform__lemma")

        count = definitions.count()

        news_vectors = google_news_vectors()

        definition_vector_keys = []
        definition_vector_vectors = []

        unknown_words = set()

        for d in tqdm(definitions.iterator(), total=count):
            keys = extract_keyed_words(d.text, news_vectors, unknown_words)
            if keys:
                vec_sum = vector_for_keys(news_vectors, keys)

                definition_vector_keys.append(definition_to_cvd_key(d))
                definition_vector_vectors.append(vec_sum)

        definition_vectors = KeyedVectors(vector_size=news_vectors.vector_size)
        definition_vectors.add_vectors(
            definition_vector_keys, definition_vector_vectors
        )
        definition_vectors.save(fspath(options["output_file"]))
