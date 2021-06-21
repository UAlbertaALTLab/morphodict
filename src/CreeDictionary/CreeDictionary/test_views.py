import logging
from http import HTTPStatus
from typing import Dict, Optional

import pytest
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
)
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertInHTML

from crkeng.app.preferences import DisplayMode, ParadigmLabel
from morphodict.lexicon.models import Wordform

# The test wants an ID that never exists. Never say never; I have no idea if we'll
# have over two billion wordforms, however, we'll most likely run into problems once
# we exceed certain storage requirements. For example, the maximum for a signed,
# 32-bit int is a possible boundary condition that may cause issues elsewhere:
ID_THAT_SHOULD_BE_TOO_BIG = str(2 ** 31 - 1)


class TestLemmaDetailsInternal4xx:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("lemma_id", "paradigm_size", "expected_code"),
        [
            ["-10", "FULL", HttpResponseBadRequest.status_code],
            ["10", None, HttpResponseBadRequest.status_code],
            ["5.2", "LINGUISTIC", HttpResponseBadRequest.status_code],
            ["123", "LINUST", HttpResponseBadRequest.status_code],
            [ID_THAT_SHOULD_BE_TOO_BIG, "FULL", HttpResponseNotFound.status_code],
        ],
    )
    def test_paradigm_details_internal_400_404(
        self, lemma_id: Optional[str], paradigm_size: Optional[str], expected_code: int
    ):
        c = Client()

        get_data: Dict[str, str] = {}
        if lemma_id is not None:
            get_data["lemma-id"] = lemma_id
        if paradigm_size is not None:
            get_data["paradigm-size"] = paradigm_size
        response = c.get(reverse("cree-dictionary-paradigm-detail"), get_data)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(("method",), (("post",), ("put",), ("delete",)))
    def test_paradigm_details_internal_wrong_method(self, method: str):
        c = Client()
        response = getattr(c, method)(
            reverse("cree-dictionary-paradigm-detail"),
            {"lemma-id": 1, "paradigm-size": "BASIC"},
        )
        assert response.status_code == HttpResponseNotAllowed.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        reverse("cree-dictionary-index"),
        reverse("cree-dictionary-search") + "?q=kotiskâwêw",
        reverse("cree-dictionary-about"),
        reverse("cree-dictionary-contact-us"),
        # Note: do NOT test word-detail page, as this page has tonnes of "errors"
        # checking for things like is_title, is_label, is_heading, etc.
    ],
)
def test_pages_render_without_template_errors(url: str, client: Client, caplog):
    """
    Ensure the index page renders without template errors.

    Note: template errors are not necessarily errors, but Django logs them anyway 🙃
    See: https://docs.djangoproject.com/en/3.1/ref/templates/api/#how-invalid-variables-are-handled
    """
    with caplog.at_level(logging.DEBUG):
        req = client.get(url)

    assert req.status_code == 200

    template_errors = [log for log in caplog.records if is_template_error(log)]
    assert len(template_errors) == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lexeme,slug_disambiguator,example_forms",
    [
        ("niya", None, ["niyanân", "kiyânaw", "kiyawâw", "wiyawâw"]),
        ("awa", "awa1", ["ôma", "awa", "ana"]),
        ("minôs", None, ["minôs", "minôsa", "niminôs"]),
    ],
)
def test_retrieve_paradigm(
    client: Client, lexeme: str, slug_disambiguator, example_forms: str
):
    """
    Test going to the lexeme details page with a paradigm.
    """
    query_args = {}
    if slug_disambiguator:
        query_args["slug"] = slug_disambiguator
    wf = Wordform.objects.get(text=lexeme, **query_args)
    url = reverse("cree-dictionary-index-with-lemma", args=[wf.slug])
    response = client.get(url)

    assert response.status_code == 200
    body = response.content.decode("UTF-8")

    assertInHTML(lexeme, body)
    for wordform in example_forms:
        assertInHTML(wordform, body)


@pytest.mark.django_db
def test_paradigm_from_full_page_and_api(client: Client):
    """
    The paradigm returned from the full details page and the API endpoint should
    contain the exact same information.
    """
    lemma_text = "wâpamêw"
    paradigm_size = "FULL"

    wordform = Wordform.objects.get(text=lemma_text)
    assert wordform.lemma == wordform, "this test requires a lemma"

    # Get standalone page:
    response = client.get(
        reverse("cree-dictionary-index-with-lemma", args=[lemma_text]),
        {"paradigm-size": paradigm_size},
    )
    assert response.status_code == HTTPStatus.OK
    standalone_html = response.content.decode("UTF-8")
    assert lemma_text in standalone_html

    # Get fragment from API request:
    response = client.get(
        reverse("cree-dictionary-paradigm-detail"),
        {
            "lemma-id": wordform.id,
            "paradigm-size": paradigm_size,
        },
    )
    assert response.status_code == HTTPStatus.OK
    html_fragment = response.content.decode("UTF-8")
    assert lemma_text in html_fragment

    assertInHTML(html_fragment, standalone_html)


@pytest.mark.parametrize("mode", DisplayMode.choices)
@pytest.mark.parametrize("whence", [None, reverse("cree-dictionary-about")])
def test_change_display_mode_sets_cookie(mode, whence, client: Client):
    """
    Changing the display mode should set some cookies and MAYBE do a redirect.
    """

    url = reverse("cree-dictionary-change-display-mode")
    headers = {}
    if whence:
        # referer (sic) is the correct spelling in HTTP
        # (spelling is not the IETF's strong suit)
        headers["HTTP_REFERER"] = whence

    res = client.post(url, {"mode": mode}, **headers)

    # morsel is Python's official term for a chunk of a cookie
    # see: https://docs.python.org/3/library/http.cookies.html#morsel-objects
    assert (morsel := res.cookies.get("mode")) is not None
    assert morsel.value == mode

    if whence:
        assert res.status_code == HTTPStatus.SEE_OTHER
        assert res.headers.get("Location") == whence
    else:
        assert res.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)


@pytest.mark.parametrize("option", ParadigmLabel.choices)
@pytest.mark.parametrize("whence", [None, reverse("cree-dictionary-about")])
def test_change_paradigm_label_preference(option, whence, client: Client):
    """
    Changing the display mode should set some cookies and MAYBE do a redirect.
    """

    url = reverse("cree-dictionary-change-paradigm-label")
    headers = {}
    if whence:
        # referer (sic) is the correct spelling in HTTP
        # (spelling is not the IETF's strong suit)
        headers["HTTP_REFERER"] = whence

    res = client.post(url, {ParadigmLabel.cookie_name: option}, **headers)

    # morsel is Python's official term for a chunk of a cookie
    # see: https://docs.python.org/3/library/http.cookies.html#morsel-objects
    assert (morsel := res.cookies.get(ParadigmLabel.cookie_name)) is not None
    assert morsel.value == option

    if whence:
        assert res.status_code == HTTPStatus.SEE_OTHER
        assert res.headers.get("Location") == whence
    else:
        assert res.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)


####################################### Helpers ########################################


def is_template_error(record: logging.LogRecord) -> bool:
    """
    Looking for an error log that looks like this:

        Exception while resolving variable 'X' in template 'Y'.
        Traceback (most recent call last):
            ...
        SomeError: error

    """
    if record.name != "django.template":
        return False

    if not record.exc_info:
        return False

    return True
