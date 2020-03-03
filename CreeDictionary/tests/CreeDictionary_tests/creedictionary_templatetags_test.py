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
    print(rendered)
    assert 'lang="cr"' in rendered
    assert 'data-orth-Latn="wâpamêw"' in rendered
    assert 'data-orth-Latn-x-macron="wāpamēw"' in rendered
    assert 'data-orth-Cans="ᐚᐸᒣᐤ"' in rendered
    assertInHTML(
        """
        <span lang="cr" data-orth data-orth-Latn="wâpamêw" data-orth-latn-x-macron="wāpamēw" data-orth-Cans="ᐚᐸᒣᐤ">wâpamêw</span>
        """,
        rendered,
    )


# TODO: test naughty things in html
