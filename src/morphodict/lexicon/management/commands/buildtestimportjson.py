import json
import logging
import os
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
)
from collections import defaultdict
from pathlib import Path
from subprocess import check_call
from unicodedata import normalize

from django.core.management import BaseCommand

from morphodict.lexicon import (
    DEFAULT_FULL_IMPORTJSON_FILE,
    DEFAULT_TEST_IMPORTJSON_FILE,
)
from morphodict.lexicon.test_db import TEST_DB_TXT_FILE, get_test_words

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Update a test importjson file from test_db_words"""

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = ArgumentDefaultsHelpFormatter

        parser.add_argument(
            "--full-importjson",
            help="The full dictionary file to read in",
            default=DEFAULT_FULL_IMPORTJSON_FILE,
        )
        parser.add_argument(
            "--test-importjson",
            help="The test dictionary file to write out",
            default=DEFAULT_TEST_IMPORTJSON_FILE,
        )
        parser.add_argument(
            "--test-db-words-file",
            help="The list of test words to use in the test dictionary",
            default=TEST_DB_TXT_FILE,
        )

    def handle(self, full_importjson, test_importjson, test_db_words_file, **options):
        full_importjson = Path(full_importjson)
        test_importjson = Path(test_importjson)
        test_db_words_file = Path(test_db_words_file)

        full_dictionary = json.loads(full_importjson.read_text())

        words = get_test_words(test_db_words_file)

        test_dictionary = TestDictionary(full_dictionary, words)
        test_json = json.dumps(
            test_dictionary.entries(), ensure_ascii=False, indent=True
        )

        (test_importjson.with_suffix(".orig")).write_text(test_json)
        test_importjson.write_text(test_json)

        check_call(
            [
                "npx",
                "--no-install",
                "prettier",
                "--write",
                "--parser=json",
                os.fspath(test_importjson),
            ]
        )


def entry_sort_key(entry):
    """
    - Sort lemmas by slug
    - Sort non-lemma wordforms by head, immediately after slug
    """
    is_lemma = "slug" in entry
    if is_lemma:
        slug = entry["slug"]
        # Empty string will sort first, before any non-lemma wordforms
        form = ""
    else:
        slug = entry["formOf"]
        form = entry["head"]

    # This isn’t quite right, but by decomposing characters, at least ‘a’s will
    # sort near each other
    slug = normalize("NFD", slug)
    form = normalize("NFD", form)

    return (slug, form)


class TestDictionary:
    def __init__(self, full_dictionary, words):
        self._full_dictionary = full_dictionary
        self._test_words = words

        # List of entries
        self._entries = []
        # set of IDs to avoid duplicates
        self._added_entries = set()

        # Track which words we haven’t yet seen
        self._unused_words = set(self._test_words)

        self._group_by_slug()
        self._extract()

    def _group_by_slug(self):
        """Create _by_slug dict mapping slugs to list of lemma and all wordforms"""
        self._by_slug = defaultdict(list)
        for entry in self._full_dictionary:
            if "slug" in entry:
                assert "formOf" not in entry
                self._by_slug[entry["slug"]].append(entry)
            elif "formOf" in entry:
                assert "slug" not in entry
                self._by_slug[entry["formOf"]].append(entry)
            else:
                raise AssertionError("Entry must contain either formOf or slug")

    def _add_entry(self, entry):
        """Add an entry from the full dictionary to the test one."""

        if id(entry) in self._added_entries:
            return

        head = entry["head"]
        self._unused_words.discard(head)
        self._entries.append(entry)
        self._added_entries.add(id(entry))

    def _extract(self):
        # An entry will be picked up if any of these apply:
        #   - It is a lemma whose head text is listed in test_db_words
        #   - It is a wordform whose head text is listed in test_db_words
        #   - It is a lemma or wordform from the same lexeme as one of the above

        for entry in self._full_dictionary:
            if entry["head"] in self._test_words:
                self._add_entry(entry)

        for entry in self._entries[:]:
            slug = entry["slug"] if "slug" in entry else entry["formOf"]
            for form in self._by_slug[slug]:
                self._add_entry(form)

        if self._unused_words:
            raise Exception(
                f"Some words from test_db_words were not extracted: {self._unused_words!r}"
            )

    def entries(self):
        return sorted(self._entries, key=entry_sort_key)
