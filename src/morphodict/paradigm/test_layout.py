from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

@pytest.mark.parametrize(
    ("lemma_text", "layout", "paradigm_size", "entries"),
    [
        ("wâpamêw", "VTA",  "full", ["kiwâpamikonaw", "ê-kî-wâpamiskik", "ê-wâpamitân", "niwâpamâw"]),
        ("kotiskâwêw", "VAI", "full", ["nikotiskâwân", "ê-wî-kotiskâwêt", "kotiskâwê", "nikotiskâwân"]),
        ("acimosis", "NA", "full", ["acimosis", "acimosisak", "kicacimosisimiwâwa"])
    ],
)
def test_paradigm_from_full_page_and_api(client: Client, lemma_text: str, paradigm_size: str, layout: str, entries: list[str]):
    """
    The paradigm returned from the full details page and the API endpoint should
    contain the exact same information.
    """
    # Get standalone page:
    response = client.get(
        reverse("morphodict-paradigm-layout"),
        {
            "paradigm-size": paradigm_size,
            "lemma":lemma_text,
            "layout": layout
        },
    )
    assert response.status_code == HTTPStatus.OK
    standalone_html = response.content.decode("UTF-8")
    for entry in entries:
        assert entry in standalone_html
