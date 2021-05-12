#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from io import StringIO

import pytest
from CreeDictionary.CreeDictionary.relabelling import Relabelling

labels = Relabelling.from_tsv(
    StringIO(
        """
FST TAG\tLINGUISTIC (SHORT)\tLINGUISTIC (LONG)\tENGLISH\tNÊHIYAWÊWIN\tEMOJI
3Sg\t3s\tActor: 3rd Person Singular\ts/he\twiya (awa) -\t
3Sg+4Sg/PlO\t\t\ts/he → him/her/them\twiya → wiya/wiyawâw (ana/aniki)\t-
4Sg/PlO\t→ 4\tGoal: 3rd Person Singular/Plural (Obviative)\t→ him/her/them\t→ wiya/wiyawâw (ana/aniki) -\t
Ind\t\tIndependent\tni-/ki- word\tni-/ki- itwêwin\t
Prs\tPresent\tPresent tense\tsomething is happening now\tê-ispayik anohc/mêkwâc/mâna\t
TA\tTransitive Animate\t\tlike: wîcihêw, itêw\ttâpiskôc: wîcihêw, itêw\t
TI\tTransitive Inaminate\t\tlike: nâtam, mîciw\ttâpiskôc: nâtam, mîciw\t
V+AI\tAnimate intransitive verb\tVerb - animate intransitive\tAction word - like: mîcisow, nipâw\tispayin-itwêwin - tâpiskôc: mîcisow, nipâw\t🧑🏽➡️💧
V+II\tInanimate intransitive verb\tVerb - inanimate intransitive\tAction word - like: miywâsin, mihkwâw\tispayin-itwêwin - tâpiskôc: miywâsin, mihkwâw\t💧➡️
V+TA\tTransitive animate verb\tVerb - transitive animate\tAction word - like: wîcihêw, itêw\tispayin-itwêwin - tâpiskôc: wîcihêw, itêw\t🧑🏽➡️🧑🏽
V+TI\tTransitive inanimate verb\tVerb - transitive inanimate\tAction word - like: nâtam, mîciw\tispayin-itwêwin - tâpiskôc: nâtam, mîciw\t🧑🏽➡️
V\tVerb\tVerb\tAction word\tispayin-itwêwin
""".lstrip()
    )
)


def test_getting_a_pos_and_word_class_label():
    label = labels.linguistic_short.get_longest(("V", "TA"))
    assert label == "Transitive animate verb"


def test_providing_an_entire_analysis_will_match_the_longest_prefix():
    label = labels.linguistic_long.get_longest(("V", "TA"))
    new_label = labels.linguistic_long.get_longest(
        ("V", "TA", "Prs", "Ind", "3Sg", "4Sg/PlO")
    )
    assert new_label == label


def test_getting_a_label_that_does_not_exist_should_return_none():
    label = labels.linguistic_short.get_longest(("Not", "Real", "Labels"))
    assert label is None


@pytest.mark.parametrize("tag", ["V", "TI", "4Sg/PlO"])
def test_it_still_works_like_get_if_given_just_one_tag(tag):
    label_from_get = labels.linguistic_short.get(tag)
    label_from_get_longest = labels.linguistic_short.get_longest((tag,))
    assert label_from_get_longest == label_from_get


@pytest.mark.parametrize("key", ["V", ("V",), ("V", "TA")])
def test_contains_tag_sets(key):
    """
    Test that we can use either a tag or a tuple of tags.
    """
    assert key in labels


def test_get_full_relabelling():
    tag_set = ("V", "TA", "Prs", "Ind", "3Sg", "4Sg/PlO")
    relabelling = labels.english.get_full_relabelling(tag_set)
    assert relabelling == [
        "Action word - like: wîcihêw, itêw",
        "something is happening now",
        "ni-/ki- word",
        "s/he → him/her/them",
    ]


def test_chunks_make_full_labels():
    tag_set = ("V", "TA", "Prs", "Ind", "3Sg", "4Sg/PlO")
    chunks = list(labels.english.chunk(tag_set))
    assert chunks == [
        ("V", "TA"),
        ("Prs",),
        ("Ind",),
        ("3Sg", "4Sg/PlO"),
    ]
