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
from collections import defaultdict
from pathlib import Path


def iter_results(input_file):
    """Return a sequence of dicts, regardless of whether file has a header or not"""
    reader = csv.reader(input_file)

    have_header = None
    column_count = None
    have_notes = False

    seen_queries = set()

    first_row = True
    for row in reader:
        print("got row", row)
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


def main():
    survey_files = (Path(__file__).parent / "survey_results").glob("*.csv")

    query_values = defaultdict(lambda term: defaultdict(0))

    for filename in survey_files:
        with open(filename, "rt", newline="") as f:
            for row in iter_results(f):
                query = row["Query"]
                values = row["Values"]


if __name__ == "__main__":
    main()
