import json
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
        parser.add_argument(
            "json_file",
            help=f"The importjson file to import",
            nargs="?",
            default=DEFAULT_IMPORTJSON_FILE,
        )

    def handle(self, json_file, crkeng_cleanup, output_file, **options):
        with open(json_file, "r") as f:
            data = json.load(f)

        if crkeng_cleanup:
            self.crkeng_cleanup(data)

        data.sort(key=entry_sort_key)

        if not output_file:
            output_file = json_file

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

        check_call(["npx", "prettier", "--parser=json", "--write", output_file])

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
