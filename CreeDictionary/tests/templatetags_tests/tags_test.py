#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Test the {% as_opspan %} tag.
"""

from django.test import SimpleTestCase
from django.template import Context, Template

# https://krzysztofzuraw.com/blog/2017/how-to-test-django-template-tags.html


class AsOASpanTemplateTagTest(SimpleTestCase):
    def test_creates_span_from_literal_text(self):
        template_to_render = Template(
            "{% load creedictionary_orthography %}" "{% as_oaspan 'tânisi' %} "
        )
        rendered_template = template_to_render.render(Context())
        self.assertInHTML(
            '<span lang="cr" data-oaspan>tânisi</span>', rendered_template
        )

    def test_creates_span_from_variable(self):
        context = Context({"text": "ê-wâpamât"})
        template_to_render = Template(
            "{% load creedictionary_orthography %}" "{% as_oaspan text %} "
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML(
            '<span lang="cr" data-oaspan>ê-wâpamât</span>', rendered_template
        )
