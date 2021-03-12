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
    # Expecting the following:
    # <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    #   <!-- primary site urls -->
    #   <url>
    #     <loc>//itwewina.altlab.app/</loc>
    #   </url>
    #
    #   <!-- head word forms -->
    #   <url>
    #     <loc>//itwewina.altlab.app/</loc>
    #   </url>
    # </urlset>
    ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [loc.text for loc in root.findall("./sitemap:url/sitemap:loc", ns)]

    # Try visiting a page:
    url = random.choice(locations)
    r = client.get(urlparse(url).path, follow=True)
    assert r.status_code == HTTPStatus.OK, f"unexpected status for {url}"


@pytest.fixture
def sitemap_url():
    return reverse("django.contrib.sitemaps.views.sitemap")
