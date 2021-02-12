"""
Get absolute URLs for static assets.
"""

from urllib.parse import ParseResult, urlparse, urlunparse

from django import template
from django.templatetags.static import StaticNode
from django.urls import reverse

register = template.Library()


class AbstaticNode(StaticNode):
    """
    {% abstatic %} is like Django's {% static %} tag,
    but always returns an absolute URI.
    """

    def url(self, context) -> str:
        url_to_asset = super().url(context)

        parsed_url = urlparse(url_to_asset)
        assert parsed_url.path

        if is_absolute_uri(parsed_url):
            return url_to_asset

        # Delegate to Django to provide its own schema and authority:
        path_and_file = urlunparse(parsed_url._replace(scheme="", netloc=""))
        return context["request"].build_absolute_uri(path_and_file)


def is_absolute_uri(url: ParseResult) -> bool:
    """
    What is an absolute URL?

    From: https://stackoverflow.com/a/17407021/6626414

    > Absolute URLs contain a great deal of information which may already be known from
    > the context of the base document's retrieval, including the scheme, network
    > location, and parts of the URL path.

    See also: https://tools.ietf.org/html/rfc1808
    """
    # netloc == authority, i.e., [username[:password]@]example.com[:443]
    if url.scheme and url.netloc:
        return True
    return False


@register.tag
def abstatic(parser, token):
    """
    Given a relative path to a static asset, return the absolute path to the
    asset.

    Derived from: https://github.com/django/django/blob/635d53a86a36cde7866b9caefeb64d809e6bfcd9/django/templatetags/static.py#L143-L159
    """
    return AbstaticNode.handle_token(parser, token)
