#!/usr/bin/env python3

"""
Get absolute URLs for static assets.
"""
from django import template
from django.urls import reverse
from django.templatetags.static import StaticNode

register = template.Library()


class AbsoluteStaticNode(StaticNode):
    def url(self, context) -> str:
        path = super().url(context)
        if not path.startswith("/"):
            # Assume it's already an absolute URI:
            return path

        return context["request"].build_absolute_uri(path)


@register.tag
def abstatic(parser, token):
    """
    Given a relative path to a static asset, return the absolute path to the
    asset.

    Derived from: https://github.com/django/django/blob/635d53a86a36cde7866b9caefeb64d809e6bfcd9/django/templatetags/static.py#L143-L159
    """
    return AbsoluteStaticNode.handle_token(parser, token)
