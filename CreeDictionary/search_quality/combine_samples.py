#!/usr/bin/env python3

"""
Combine samples in survey_results directory into one

The algorithm is:

 1. For each word list:
     1. For each query term, assign 1/n points to the n’th result.
         For example, if the list has "foo: bar, baz, qux", then "bar" gets 1
         point, "baz" gets 1/2 point, and "qux" gets 1/3 point as results for
         "foo"
 2. For each query term:
      1. Add up all the points for all the results across all lists
      2. Sort by highest points first
"""
import csv
from argparse import ArgumentParser, BooleanOptionalAction
from collections import defaultdict
from io import StringIO
from pathlib import Path

from CreeDictionary.search_quality import SURVEY_DIR


def iter_results(input_file):
    """Yield dicts for rows from a CSV file, whether it has a header or not

    The reason we don’t just add a header to every .csv file and use DictReader
    is that these .csv files may have arbitrarily many columns.
    """
    reader = csv.reader(input_file)

    have_header = None
    column_count = None
    have_notes = False

    seen_queries = set()

    first_row = True
    for row_index, row in enumerate(reader):
        if first_row:
            first_row = False

            have_header = row[0].lower().strip() == "query"
            if have_header:
                column_count = len(row)
            if have_header and row[-1].lower().strip() == "notes":
                if row[-2].strip():
                    raise Exception("Must have blank column before notes column")
                have_notes = True

            if have_header:
                # Don’t yield first line
                continue

        if have_header:
            if len(row) > column_count:
                raise Exception(f"More entries in row {row} than header values")

        query_term = row[0].strip()
        # max_col may be None here, but that’s ok, because `row[1:None]` is
        # the Python way of saying `row[1:]` when the blank in the middle
        # of `:]` is actually a variable in `row[1:max_col]` below.
        max_col = column_count
        if have_notes:
            if row[column_count - 2].strip():
                raise Exception("Must have blank column before notes column")
            max_col = column_count - 2

        values = row[1:max_col]
        while not values[-1].strip():
            values = values[:-1]

        if query_term in seen_queries:
            raise Exception(f"Duplicate query term {query_term}")
        seen_queries.add(query_term)

        yield {"Query": query_term, "Values": values}


def combine_results(result_lists):
    points = defaultdict(int)
    for results in result_lists:
        for i, result in enumerate(results):
            points[result] += 1 / (i + 1)

    def by_points_then_length_then_alphabetical(result):
        """
        First, sort by most points. Break ties using the heuristic, “shorter
        words are easier and most likely what people want to see first,” then
        fall back to alphabetical.
        """
        return (-points[result], len(result), result)

    return sorted(points.keys(), key=by_points_then_length_then_alphabetical)


class SurveyCollection:
    def __init__(self, survey_dir=SURVEY_DIR):
        self.survey_dir = survey_dir
        self.queries = defaultdict(list)

        self._load()

    def _load(self):
        survey_files = self.survey_dir.glob("*.csv")

        for filename in survey_files:
            with open(filename, "rt", newline="") as f:
                for row in iter_results(f):
                    values = row["Values"]
                    query = row["Query"]
                    self.queries[query].append(values)

    def combined_results_for(self, query):
        results = self.queries[query]
        return combine_results(results)

    def combined_results(self):
        for query, results in self.queries.items():
            combined = combine_results(results)
            yield query, combined


def main():
    script_dir = Path(__file__).parent

    parser = ArgumentParser(
        description="""
        Use ranked voting to combine files in survey_sample/*.csv into
        sample.csv.
        """
    )
    parser.add_argument("--write", action=BooleanOptionalAction, default="yes")
    parser.add_argument("--output-file", default=script_dir / "sample.csv")
    args = parser.parse_args()

    output_text = StringIO(newline="")

    class LfDialect(csv.excel):
        "Avoid git warning, “CRLF will be replaced by LF”"
        lineterminator = "\n"

    csv_out = csv.writer(output_text, dialect=LfDialect)
    csv_out.writerow(["Query", "Nêhiyawêwin 1", "Nêhiyawêwin 2", "Nêhiyawêwin 3"])

    survey_collection = SurveyCollection()
    for query, combined in survey_collection.combined_results():
        csv_out.writerow([query] + combined[:3])

    if args.write:
        Path(args.output_file).write_text(output_text.getvalue())
        print(f"Wrote to {args.output_file}")
    else:
        print(output_text.getvalue())


if __name__ == "__main__":
    main()
