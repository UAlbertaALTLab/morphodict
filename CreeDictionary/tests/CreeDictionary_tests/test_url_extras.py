#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from django.http import HttpRequest
from django.template import RequestContext, Context, Template


def test_orth_template_tag():
    """
    Test that the {% abstatic %} tag returns a static path.
    """
    asset = "CreeDictionary/favicon.ico"

    request = HttpRequest()
    request.META.setdefault("HTTP_HOST", "example.com")

    django_builtin_static = Template(
        "{% load static %}" "{% static '" + asset + "' %}"
    ).render(Context({}))
    assert not django_builtin_static.startswith("http")

    context = RequestContext(request, {})
    template = Template("{% load url_extras %}" "{% abstatic '" + asset + "' %}")
    rendered = template.render(context)

    assert rendered.startswith("http")
    assert rendered.endswith(django_builtin_static)
