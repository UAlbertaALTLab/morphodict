#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from django.http import HttpRequest
from django.template import RequestContext, Context, Template


def test_abstatic():
    """
    Test that the {% abstatic %} tag returns a static path.
    """
    asset = "frontend/favicon.ico"

    django_builtin_static = render_builtin_django_static(asset)
    assert not django_builtin_static.startswith("http")

    abstatic_url = render_with_abstatic(asset)
    assert abstatic_url.startswith("http")
    assert abstatic_url.endswith(django_builtin_static)
    assert abstatic_url != django_builtin_static


def test_abstatic_static_url_set(settings):
    """
    When STATIC_URL is set to an absolute URI, {% abstatic %} should be identical to
    Django's builtin {% static %}.
    """
    settings.STATIC_URL = "https://cdn.example.com"

    asset = "frontend/favicon.ico"

    django_builtin_static = render_builtin_django_static(asset)
    abstatic_url = render_with_abstatic(asset)
    assert abstatic_url == django_builtin_static


def render_with_abstatic(asset: str) -> str:
    request = HttpRequest()
    request.META.setdefault("HTTP_HOST", "example.com")

    context = RequestContext(request, {})
    template = Template("{% load url_extras %}" "{% abstatic '" + asset + "' %}")
    return template.render(context)


def render_builtin_django_static(asset: str) -> str:
    template = Template("{% load static %}" "{% static '" + asset + "' %}")
    return template.render(Context())
