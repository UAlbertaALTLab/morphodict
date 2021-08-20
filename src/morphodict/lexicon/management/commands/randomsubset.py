import json
import logging
import os
import random
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
)
from pathlib import Path
from subprocess import check_call

from django.core.management import BaseCommand

from morphodict import morphodict_language_pair
from morphodict.lexicon import (
    DEFAULT_FULL_IMPORTJSON_FILE,
)
from morphodict.lexicon.management.commands.buildtestimportjson import entry_sort_key

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Extract a random subset of a full dictionary for testing"""

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        parser.add_argument(
            "--full-importjson",
            help="The full dictionary file to read in",
            default=DEFAULT_FULL_IMPORTJSON_FILE,
        )
        parser.add_argument(
            "--output-importjson",
            help="The test dictionary file to write out",
            default=DEFAULT_FULL_IMPORTJSON_FILE.with_stem(
                f"{morphodict_language_pair()}_subset_dictionary"
            ),
        )
        parser.add_argument(
            "--percentage",
            type=float,
            help="What % of words to keep",
            default=10,
        )

    def handle(self, full_importjson, output_importjson, percentage, **options):
        fraction = percentage / 100

        full_importjson = Path(full_importjson)

        full_dictionary = json.loads(full_importjson.read_text())
        full_dictionary.sort(key=entry_sort_key)

        new_entries = []

        # formOf entries are kept iff the parent was kept. The sort order of
        # entry_sort_key ensures that all non-lemma wordforms are seen as a
        # group immediately after their corresponding lemmas.
        kept_previous = None
        for entry in full_dictionary:
            if "formOf" in entry:
                if kept_previous:
                    new_entries.append(entry)
            else:
                should_keep = random.random() <= fraction
                if should_keep:
                    new_entries.append(entry)

                kept_previous = should_keep

        output_importjson = Path(output_importjson)
        output_importjson.write_text(
            json.dumps(new_entries, ensure_ascii=False, indent=True, sort_keys=True)
        )

        check_call(
            [
                "npx",
                "--no-install",
                "prettier",
                "--write",
                "--parser=json",
                os.fspath(output_importjson),
            ]
        )
