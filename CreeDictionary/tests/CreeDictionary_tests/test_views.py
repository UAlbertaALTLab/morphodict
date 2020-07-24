from typing import Dict, Optional

import pytest
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.test import Client


class TestLemmaDetailsInternal4xx:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("lemma_id", "paradigm_size", "expected_code"),
        [
            ["-10", "FULL", HttpResponseBadRequest.status_code],
            ["10", None, HttpResponseBadRequest.status_code],
            ["5.2", "LINGUISTIC", HttpResponseBadRequest.status_code],
            ["123", "LINUST", HttpResponseBadRequest.status_code],
            [
                "99999999",
                "FULL",
                HttpResponseNotFound.status_code,
            ],  # we'll never have as many as 99999999 entries in the database so it's a non-existent id
        ],
    )
    def test_lemma_details_internal_400_404(
        self, lemma_id: Optional[str], paradigm_size: Optional[str], expected_code: int
    ):
        c = Client()

        get_data: Dict[str, str] = {}
        if lemma_id is not None:
            get_data["lemma-id"] = lemma_id
        if paradigm_size is not None:
            get_data["paradigm-size"] = paradigm_size
        response = c.get("/_lemma_details/", get_data)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(("method",), (("post",), ("put",), ("delete",)))
    def test_lemma_details_internal_wrong_method(self, method: str):
        c = Client()
        response = getattr(c, method)(
            "/_lemma_details/", {"lemma-id": 1, "paradigm-size": "BASIC"}
        )
        assert response.status_code == HttpResponseNotAllowed.status_code
