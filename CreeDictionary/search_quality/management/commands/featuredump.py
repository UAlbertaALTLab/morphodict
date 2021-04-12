import json
import random
from argparse import ArgumentParser, BooleanOptionalAction

from django.core.management import BaseCommand

from API.search import search
from ... import DEFAULT_SAMPLE_FILE
from ...sample import load_sample_definition


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--csv-file", default=DEFAULT_SAMPLE_FILE)
        parser.add_argument("--max", type=int, help="Only run this many queries")
        parser.add_argument(
            "--shuffle",
            action=BooleanOptionalAction,
            help="Shuffle sample before running, useful with --max",
        )

    def handle(self, *args, **options):
        samples = load_sample_definition(options["csv_file"])
        if options["shuffle"]:
            random.shuffle(samples)
        if options["max"] is not None:
            samples = samples[:max]

        for entry in samples:
            query = entry["Query"]
            for i, r in enumerate(search(query=f"verbose:1 {query}")._results.values()):
                ret = json.loads(r.features_json())
                ret["query"] = query
                ret["candidate_number"] = i
                ret["wordform_text"] = r.wordform.text
                ret["lemma_wordform"] = r.wordform.lemma.text
                ret["is_lemma"] = 1 if r.is_lemma else 0
                print(json.dumps(ret, ensure_ascii=False))
