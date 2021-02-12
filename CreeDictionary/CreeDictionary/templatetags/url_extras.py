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
        path_and_file = to_pf_url(parsed_url)
        return context["request"].build_absolute_uri(path_and_file)


def is_absolute_uri(url: ParseResult) -> bool:
    """
    Returns True if the parsed result is an "absolute URI".

    We define an "absolute URI" as containing at mimimum a **scheme** and an
    **host** (a.k.a., an authority).

    It must contain SH according to the nomenclature defined in this proposal:
    https://gist.github.com/andrewdotn/eebeaa60d48c3c0f6f9fc75f0ede8d03#proposal

    Examples of absolute URIs:
        [SH  ]  https://example.com
        [SHP ]  https://example.com/
        [SHPF]  https://example.com/foo/cat.gif

    What are NOT absolute URIs:
        [   F]  cat.gif
        [  P ]  /
        [  PF]  /foo/cat.gif
        [ HPF]  //example.com/foo/cat.gif†
        [S  F]  https:cat.gif (uncommon)
        [S PF]  https:/foo/cat.gif (uncommon)

    †: This is called a "network-path reference, and relies on inferring the scheme
       based on an existing base URI. For our purposes, this is not "absolute" enough!
       Source: https://tools.ietf.org/html/rfc3986#section-4.2

    """
    # netloc == authority, i.e., [username[:password]@]example.com[:443]
    if url.scheme and url.netloc:
        return True
    return False


def to_pf_url(url: ParseResult):
    """
    Returns *P*ath and *F*ile as defined here:
    https://gist.github.com/andrewdotn/eebeaa60d48c3c0f6f9fc75f0ede8d03#proposal
    """
    return urlunparse(url._replace(scheme="", netloc=""))


@register.tag
def abstatic(parser, token):
    """
    Given a relative path to a static asset, return the absolute path to the
    asset.

    Derived from: https://github.com/django/django/blob/635d53a86a36cde7866b9caefeb64d809e6bfcd9/django/templatetags/static.py#L143-L159
    """
    return AbstaticNode.handle_token(parser, token)
