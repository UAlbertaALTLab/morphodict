"""
Get absolute URLs for static assets.
"""
from typing import Optional

from django import template
from django.templatetags.static import StaticNode
from django.urls import reverse

register = template.Library()


class AbsoluteURLStaticNode(StaticNode):
    """
    Like Django's {% static %} tag, but always returns an absolute URL.
    """

    def url(self, context) -> str:
        component = super().url(context)
        if is_absolute_url(component):
            return component

        # Django say "absolute_uri" but they really mean "absolute_url" ;)
        return context["request"].build_absolute_uri(component)


def is_absolute_url(component: str) -> bool:
    """
    What is an absolute URL?

    From: https://stackoverflow.com/a/17407021/6626414

    > Absolute URLs contain a great deal of information which may already be known from
    > the context of the base document's retrieval, including the scheme, network 
    > location, and parts of the URL path.

    See also: https://tools.ietf.org/html/rfc1808
    """
    if not component.startswith("/"):
        assert component.startswith("http"), f"Not an absolute URL: {component!r}"
        assert ":" in component, f"Not an absolute URL: {component!r}"
        return True
    return False


@register.tag
def abstatic(parser, token):
    """
    Given a relative path to a static asset, return the absolute path to the
    asset.

    Derived from: https://github.com/django/django/blob/635d53a86a36cde7866b9caefeb64d809e6bfcd9/django/templatetags/static.py#L143-L159
    """
    return AbsoluteURLStaticNode.handle_token(parser, token)
