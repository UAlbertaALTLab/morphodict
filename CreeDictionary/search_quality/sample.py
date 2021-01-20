import csv
import gzip
import json
import time
from os import PathLike
from typing import Iterable, TypedDict

from API.models import Wordform
from . import SampleSearchResultsJson, DEFAULT_SAMPLE_FILE


class SampleCsvRow(TypedDict):
    English: str
    Nêhiyawêwin_1: str
    Nêhiyawêwin_2: str
    Nêhiyawêwin_3: str
    Poor_result: str
    Notes: str


SampleDefinition = Iterable[SampleCsvRow]


def dict_with_spaces_in_keys_to_underscores(d: dict):
    return {k.replace(" ", "_"): v for k, v in d.items()}


def load_sample_definition(input_file) -> SampleDefinition:
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            yield dict_with_spaces_in_keys_to_underscores(row)


def gen_run_sample(sample_file: PathLike = DEFAULT_SAMPLE_FILE, *, out_file: PathLike):
    "Run the sample, yielding status messages"

    combined_results: SampleSearchResultsJson = {}

    for entry in load_sample_definition(sample_file):
        query = entry["English"]

        # If we were being rigorous about timing, we’d run all the queries
        # multiple times in randomized orders to spread out the effects of
        # warmup and cachine
        start_time = time.time()
        results = [r.serialize() for r in Wordform.search_with_affixes(query)]
        time_taken = time.time() - start_time

        combined_results[query] = {
            "time_taken_seconds": time_taken,
            "results": results,
        }

        count = sum(1 if r["is_lemma"] else 2 for r in results)
        yield f"{count:,} results for ‘{query}’ in {time_taken:0.3}s"

    # "wt" because although gzip is a binary file format, json.dump is going to
    # want to write a string inside it
    with gzip.open(out_file, "wt") as out:
        json.dump(combined_results, out, ensure_ascii=False, indent=2)
