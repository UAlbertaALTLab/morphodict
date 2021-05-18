#!/usr/bin/env python3

"""
Pragmatical utilities thar parses and edits crk.altlabel.tsv
"""

import csv
import sys
from argparse import ArgumentParser
from pathlib import Path

# Figure out shared_res_dir
add_to_path = Path(__file__).parent.parent / "src" / "CreeDictionary"
assert add_to_path.is_dir()
sys.path.insert(0, str(add_to_path))
shared_res_dir = __import__("utils").shared_res_dir


if __name__ == "__main__":
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command_name")
    format_parser = subparsers.add_parser(
        "format", help="ensure each line has the same number of tabs."
    )

    args = parser.parse_args()

    if args.command_name == "format":
        rows = []  # type: ignore
        altblabel_tsv_path = shared_res_dir / "crk.altlabel.tsv"

        with open(altblabel_tsv_path, newline="", encoding="UTF-8") as file:
            rows.extend(csv.reader(file, delimiter="\t"))
        max_length = len(max(rows, key=len))

        new_rows = [r + ["" for _ in range(max_length - len(r))] for r in rows]
        assert all(len(row) == max_length for row in new_rows)

        print(f"New crk.altlabel.tsv written with {max_length} columns on each row")

        with open(altblabel_tsv_path, "w", newline="", encoding="UTF-8") as file:
            writer = csv.writer(file, delimiter="\t", lineterminator="\n")
            writer.writerows(new_rows)
