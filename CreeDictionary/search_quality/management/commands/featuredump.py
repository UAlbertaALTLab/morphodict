import json
import random
from argparse import ArgumentParser, BooleanOptionalAction

from django.core.management import BaseCommand
from django.db.models import prefetch_related_objects
from tqdm import tqdm

from API.search import search
from ... import DEFAULT_SAMPLE_FILE
from ...combine_samples import SurveyCollection
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
            samples = samples[: options["max"]]

        survey_collection = SurveyCollection()

        for entry in tqdm(samples):
            query = entry["Query"]

            survey = survey_collection.combined_results_for(query)
            top3 = survey[:3]

            results = search(query=f"verbose:1 cvd:1 {query}")._results.values()
            try:
                prefetch_related_objects(
                    [r.wordform for r in results], "definitions__citations"
                )
            except AttributeError:
                # seems to be a django bug?
                pass
            for i, r in enumerate(results):
                ret = json.loads(r.features_json())
                ret["query"] = query
                ret["candidate_number"] = i
                ret["wordform_text"] = r.wordform.text
                ret["definitions"] = [
                    [d.text, ", ".join(c.abbrv for c in d.citations.all())]
                    for d in r.wordform.definitions.all()
                ]
                ret["lemma_wordform"] = r.wordform.lemma.text
                ret["keyword_match_len"] = len(r.target_language_keyword_match)
                ret["is_lemma"] = 1 if r.is_lemma else 0
                ret["is_top3"] = r.wordform.text in top3
                ret["is_in_survey"] = r.wordform.text in survey
                print(json.dumps(ret, ensure_ascii=False))
