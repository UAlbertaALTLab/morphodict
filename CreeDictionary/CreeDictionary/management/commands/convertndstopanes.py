"""
Converts all loaded paradigm templates and outputs them in the pane-style template.

Note: this code is **temporary**! (2021-04-23)
"""

import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

from django.core.management import BaseCommand
from utils import ParadigmSize, WordClass, shared_res_dir  # type: ignore

from CreeDictionary.paradigm.generation import paradigm_filler  # type: ignore
from CreeDictionary.relabelling import LABELS, _LabelFriendliness  # type: ignore


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "outdir",
            nargs="?",
            help="where to save the new panes",
        )

    def handle(self, *args, **options):
        from pprint import pprint

        existing_paradigms = paradigm_filler()
        english_templates = snoop_all_plain_english_templates(existing_paradigms)
        label_to_tag = snoop_unambiguous_plain_english_tags()

        raise NotImplementedError("now to draw the rest of the owl...")


def snoop_unambiguous_plain_english_tags():
    """
    Peer into relabelling to convert linguistic labels back to tags.
    """

    from CreeDictionary.relabelling import _LabelFriendliness  # type: ignore

    label_to_tags = defaultdict(list)
    for tag, relabellings in LABELS._data.items():
        label = relabellings.get(_LabelFriendliness.ENGLISH)
        if label is None:
            lazy_log("No English label for", tag)
            continue
        label_to_tags[label].append(tag)

    label_to_unambiguous_tag = {}
    for label, tags in label_to_tags.items():
        if len(tags) == 1:
            label_to_unambiguous_tag[label] = tags[0]
        else:
            lazy_log("Ambiguous label:", label)
            lazy_log("   => maps to", tags)

    return label_to_unambiguous_tag


def snoop_all_plain_english_templates(filler):
    """
    Peers into ParadigmFiller's private internal data structures to recover ONLY the
    plain English paradigms.
    """
    desired_layouts = {}
    for (wordclass, category), layout in filler._layout_tables.items():
        if category is not ParadigmSize.FULL:
            continue
        desired_layouts[wordclass] = layout

    return desired_layouts


def lazy_log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
