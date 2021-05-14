import csv

from typing import TypedDict


class SampleCsvRow(TypedDict):
    Query: str
    Nêhiyawêwin_1: str
    Nêhiyawêwin_2: str
    Nêhiyawêwin_3: str
    Poor_result: str
    Notes: str


SampleDefinition = list[SampleCsvRow]


def dict_with_spaces_in_keys_to_underscores(d: dict):
    return {k.replace(" ", "_"): v for k, v in d.items()}


def load_sample_definition(input_file) -> SampleDefinition:
    queries = []
    seen = set()
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for i, row in enumerate(reader):
            to_yield = dict_with_spaces_in_keys_to_underscores(row)
            queries.append(to_yield)
            if to_yield["Query"] in seen:
                raise Exception(
                    f"Duplicate query: {to_yield['Query']!r} on line {i + 1}"
                )
            else:
                seen.add(to_yield["Query"])

    return queries
