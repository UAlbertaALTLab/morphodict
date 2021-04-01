from argparse import ArgumentParser

from django.core.management import BaseCommand

from ... import DEFAULT_SAMPLE_FILE, RESULTS_DIR
from ...run_sample import gen_run_sample


class Command(BaseCommand):
    help = """Run all the queries in a sample file and save the result

    The resulting json.gz file can later be analyzed for quality of the search
    results, and results run at different times and with different search
    algorithms can be compared.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("--csv-file", default=DEFAULT_SAMPLE_FILE)
        parser.add_argument(
            "--query-results-file", default=RESULTS_DIR / "query-results.json.gz"
        )

    def handle(self, *args, **options):
        for status in gen_run_sample(
            options["csv_file"], out_file=options["query_results_file"]
        ):
            self.stdout.write(status)
        self.stdout.write(f"Output written to {options['query_results_file']}")
