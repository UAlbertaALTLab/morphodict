#!/usr/bin/env python3
import csv
from argparse import ArgumentParser

from utils import shared_res_dir

if __name__ == "__main__":
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command_name")
    format_parser = subparsers.add_parser(
        "format", help="ensure each line has the same number of tabs."
    )

    args = parser.parse_args()

    if args.command_name == "format":

        rows = []
        altblabel_tsv_path = shared_res_dir / "crk.altlabel.tsv"

        with open(altblabel_tsv_path) as file:
            for row in csv.reader(file, delimiter="\t"):
                rows.append(row)
        max_length = len(max(rows, key=len))

        new_rows = [r + ["" for _ in range(max_length - len(r))] for r in rows]

        print(
            "New crk.altlabel.tsv written with %s columns on each row"
            % len(new_rows[0])
        )

        with open(altblabel_tsv_path, "w") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerows(new_rows)
