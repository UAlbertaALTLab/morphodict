import csv
from typing import Iterable, TypedDict


class SampleCsvRow(TypedDict):
    Query: str
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
