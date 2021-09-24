import json
import subprocess
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
    BooleanOptionalAction,
)
from subprocess import check_call

from django.core.management import BaseCommand

from morphodict.lexicon import DEFAULT_IMPORTJSON_FILE
from morphodict.lexicon.management.commands.buildtestimportjson import entry_sort_key


class Command(BaseCommand):
    help = """Sort an importjson file

    Sorting a file makes it easier to compare different versions of the same
    dictionary.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        parser.add_argument(
            "--crkeng-cleanup",
            action=BooleanOptionalAction,
            default=False,
            help="""
                Delete certain keys that are present but unused in the original
                crkeng importjson file.
            """,
        )
        parser.add_argument(
            "--output-file",
            help="Write output to this file, instead of overwriting the input",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--git-files",
            action="store_true",
            help="Sort all importjson files known to git",
        )
        group.add_argument(
            "json_files",
            help=f"The importjson file(s) to import",
            nargs="*",
            default=[DEFAULT_IMPORTJSON_FILE],
        )

    def handle(self, json_files, git_files, crkeng_cleanup, output_file, **options):
        has_output_file = output_file is not None
        if (git_files or len(json_files) != 1) and has_output_file:
            raise Exception(
                "Error: cannot specify --output-file option when there are multiple input files"
            )

        output_files = []
        if git_files:
            git_files = subprocess.check_output(["git", "ls-files", "-z"])
            for filename_bytes in git_files.split(b"\0"):
                if filename_bytes.endswith(b".importjson"):
                    output_files.append(filename_bytes)

        for json_file in json_files:
            with open(json_file, "r") as f:
                data = json.load(f)

            if crkeng_cleanup:
                self.crkeng_cleanup(data)

            data.sort(key=entry_sort_key)

            if not has_output_file:
                output_file = json_file

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

            output_files.append(output_file)

        check_call(["npx", "prettier", "--parser=json", "--write"] + output_files)

    def crkeng_cleanup(self, data):
        for entry in data:
            if "definesFstTag" in entry:
                # We intend to use this key, but currently don’t, and at the
                # time of writing this comment, the current values are not
                # correct in any existing importjson files.
                del entry["definesFstTag"]

            if linguistInfo := entry.get("linguistInfo", None):
                for unused_key in [
                    "as_is",
                    "inflectional_category_linguistic",
                    "inflectional_category_plain_english",
                    "wordclass_emoji",
                    "smushedAnalysis",
                ]:
                    if unused_key in linguistInfo:
                        del linguistInfo[unused_key]
