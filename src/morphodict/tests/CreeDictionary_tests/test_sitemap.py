"""
Test that the sitemap is accessible and has expected results.
"""

import random
import xml.etree.ElementTree as ET
from http import HTTPStatus
from urllib.parse import urlparse

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_can_access_sitemap(client, sitemap_url):
    assert sitemap_url == "/sitemap.xml"

    r = client.get(sitemap_url)
    assert r.status_code == HTTPStatus.OK
    assert "xml" in r["Content-Type"]


@pytest.mark.django_db
def test_sitemap_has_valid_locations(client, sitemap_url):
    r = client.get(sitemap_url)

    root = ET.fromstring(r.content)
    urls = [loc.text for loc in find_all_location_elements(root)]

    # Try visiting a page:
    url = random.choice(urls)
    r = client.get(urlparse(url).path, follow=True)
    assert r.status_code == HTTPStatus.OK, f"unexpected status for {url}"


@pytest.fixture
def sitemap_url():
    return reverse("django.contrib.sitemaps.views.sitemap")


def find_all_location_elements(root):
    """
    Given the following markup:

        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <!-- primary site urls -->
          <url>
            <loc>http://itwewina.altlab.app/</loc>
          </url>

          <!-- head word forms -->
          <url>
            <loc>http://itwewina.altlab.app/word/atim/</loc>
          </url>
        </urlset>

    Returns all <loc> elements:
    <loc>http://itwewina.altlab.app/</loc>
    <loc>http://itwewina.altlab.app/word/atim/</loc>
    """
    # The ElementTree API is... not great.
    # Whenever I get an XML document and it uses namespaces,
    # and I try to query it, I always forget that the tagname has to be QName
    # like: <http://www.sitemaps.org/schemas/sitemap/0.9:url>
    # or: <http://www.sitemaps.org/schemas/sitemap/0.9:loc>
    # this namespace
    namespace_aliases = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    # XPath to return all <loc>s within all <url>s from the current node.
    return root.findall("./sitemap:url/sitemap:loc", namespace_aliases)
