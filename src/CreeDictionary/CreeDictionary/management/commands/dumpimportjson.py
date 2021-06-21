import argparse
import json
import logging
import os
import re
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from subprocess import check_call

from django.core.management.base import BaseCommand

from CreeDictionary.API.models import Wordform, Definition
from CreeDictionary.CreeDictionary.relabelling import LABELS
from CreeDictionary.utils.fst_analysis_parser import partition_analysis
from morphodict.lexicon import DEFAULT_IMPORTJSON_FILE
from morphodict.lexicon.test_db import get_test_words, TEST_DB_IMPORTJSON

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Export data in new importjson format

    Until the new dictionary is fully ready, this takes the xml-imported data
    from the database, together with all the inferred display stuff like wc and
    ic, and exports it in the new format.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
        parser.add_argument(
            "--output-file",
            default=DEFAULT_IMPORTJSON_FILE,
            help="Where to save the output",
        )
        parser.add_argument(
            "--test-db-output-file",
            default=TEST_DB_IMPORTJSON,
            help="Where to save the test db output",
        )

    def handle(self, *args, output_file, test_db_output_file, **options):
        export = Export()
        export.add_lemmas()
        export.assign_slugs()
        export.add_non_lemmas_with_definitions()

        def prettier_json(path):
            logger.info("Running prettier…")
            check_call(["npx", "prettier", "--write", "--parser=json", os.fspath(path)])

        Path(output_file).write_text(export.as_json())
        prettier_json(output_file)
        logger.info(f"Wrote {output_file}.")

        Path(test_db_output_file).write_text(export.test_db_as_json())
        prettier_json(test_db_output_file)
        logger.info(f"Wrote {test_db_output_file}.")


def str2slug(s):
    return re.sub(r"[^a-zA-Zâêîôû-]+", "_", s)


def unsmush_analysis(analysis):
    if not analysis:
        return None

    prefix_tags, lemma, suffix_tags = partition_analysis(analysis)
    # partition_analysis returns things like [[], 'foo', ['N', 'A', 'D']]
    prefix_tags = [t + "+" for t in prefix_tags]
    suffix_tags = ["+" + t for t in suffix_tags]
    return (prefix_tags, lemma, suffix_tags)


class Export:
    def __init__(self):
        self._entries = []
        self._entries_by_wordform_id = {}

        self._used_slugs = set()

    def add_lemma_entry(self, wf, e):
        self._entries_by_wordform_id[wf.id] = e
        self._entries.append(e)

    def add_non_lemma_entry(self, wf, e):
        # Must be called after slugs are assigned!
        e["formOf"] = self._entries_by_wordform_id[wf.lemma.id]["slug"]
        self._entries.append(e)

    def _use_slug(self, slug):
        """Raise an error if this slug has already been used."""
        if slug in self._used_slugs:
            raise Exception(f"{slug=} has already been used.")
        self._used_slugs.add(slug)

    def assign_slugs(self):
        entries_by_slug = defaultdict(list)
        for e in self._entries:
            entries_by_slug[str2slug(e["head"])].append(e)

        for slug, entries in entries_by_slug.items():
            if len(entries) == 1:
                entries[0]["slug"] = slug
                self._use_slug(slug)
            else:

                def ic_slug(entry):
                    return (
                        slug
                        + "-"
                        + entry["linguistInfo"]["inflectional_category"].lower()
                    )

                by_ic = map(ic_slug, entries)
                if len(set(by_ic)) == len(entries):
                    for e in entries:
                        entry_slug = ic_slug(e)
                        e["slug"] = entry_slug
                        self._use_slug(entry_slug)
                else:
                    for i, e in enumerate(entries):
                        entry_slug = ic_slug(e) + str(i + 1)
                        e["slug"] = entry_slug
                        self._use_slug(entry_slug)

    def as_json(self):
        return json.dumps(self._entries, ensure_ascii=False, indent=2) + "\n"

    def test_db_as_json(self):
        test_db_words = get_test_words()
        remaining_test_words = set(test_db_words)

        test_entries = []
        slugs_to_grab = set()
        grabbed_slugs = set()
        for e in self._entries:
            if e["head"] in test_db_words:
                remaining_test_words.discard(e["head"])
                test_entries.append(e)
                if "formOf" in e:
                    # this is a sub-entry; make a note to grab the parent
                    slugs_to_grab.add(e["formOf"])
                else:
                    grabbed_slugs.add(e["slug"])
        for e in self._entries:
            if (
                "slug" in e
                and e["slug"] in slugs_to_grab
                and e["slug"] not in grabbed_slugs
            ):
                test_entries.append(e)

        if remaining_test_words:
            raise Exception(
                "Some entries from test_db_words.text were not found in the database: "
                + ", ".join(w for w in sorted(remaining_test_words))
            )

        return json.dumps(test_entries, ensure_ascii=False, indent=2) + "\n"

    def add_lemmas(self):
        for wf in Wordform.objects.filter(is_lemma=True).prefetch_related(
            "definitions__citations"
        ):
            paradigm = wf.paradigm or wf.wordclass_text
            if paradigm == "IPC":
                paradigm = None

            analysis = unsmush_analysis(wf.analysis)
            # In importjson, headwords are only indexed for source-language
            # search if analysis is None, on the presumption that anything with
            # an analysis can be recognized by the relaxed analyzer FST.
            #
            # The XML import process makes up analyses for ‘as-is’ entries,
            # making unanalyzable entries unsearchable. Leave these analyses
            # out.
            if wf.as_is:
                analysis = None

            entry = {
                "head": wf.text,
                "analysis": analysis,
                "paradigm": paradigm,
                "senses": [
                    {
                        "definition": d.text,
                        "sources": [c.abbrv for c in d.citations.all()],
                    }
                    for d in wf.definitions.filter(
                        auto_translation_source_id__isnull=True
                    )
                ],
                "linguistInfo": {
                    "as_is": wf.as_is,
                    "inflectional_category": wf.inflectional_category,
                    "inflectional_category_plain_english": LABELS.english.get(
                        wf.inflectional_category
                    ),
                    "inflectional_category_linguistic": LABELS.linguistic_long.get(
                        wf.inflectional_category
                    ),
                    "pos": wf.pos,
                    "stem": wf.stem,
                    "smushedAnalysis": wf.analysis,
                    "wordclass": wf.wordclass_text,
                    "wordclass_emoji": wf.get_emoji_for_cree_wordclass(),
                },
            }
            if wf.inflectional_category == "IPV":
                entry["definesFstTag"] = f"PV/{wf.text.rstrip('-')}+"

            self.add_lemma_entry(wf, entry)

    def add_non_lemmas_with_definitions(self):
        non_lemma_non_auto_definitions = Definition.objects.filter(
            wordform__is_lemma=False, auto_translation_source__isnull=True
        ).select_related("wordform")
        ids_of_non_lemma_wordforms_with_definitions = {
            d.wordform.id for d in non_lemma_non_auto_definitions
        }
        for wf in Wordform.objects.filter(
            id__in=ids_of_non_lemma_wordforms_with_definitions
        ):
            self.add_non_lemma_entry(
                wf,
                {
                    "head": wf.text,
                    "analysis": unsmush_analysis(wf.analysis),
                    "senses": [
                        {
                            "definition": d.text,
                            "sources": [c.abbrv for c in d.citations.all()],
                        }
                        for d in wf.definitions.filter(
                            auto_translation_source_id__isnull=True
                        )
                    ],
                },
            )
