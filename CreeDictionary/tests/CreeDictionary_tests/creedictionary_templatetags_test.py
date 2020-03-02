#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from django.template import Context, Template
from pytest_django.asserts import assertInHTML


def test_can_it_be_imported():
    from CreeDictionary.templatetags.creedictionary_extras import orth

    # that's it!


def test_produces_correct_markup():
    context = Context({"wordform": "wâpamêw"})
    template = Template("{% load creedictionary_extras %}" "{{ wordform | orth }}")

    rendered = template.render(context)
    assertInHTML('data-orth-Latn="wâpamêw"', rendered)
