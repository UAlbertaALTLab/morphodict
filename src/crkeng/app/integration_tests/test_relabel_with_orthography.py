import pytest
from django.http import HttpRequest
from django.template import RequestContext, Template

from morphodict.orthography.utils import to_macrons, to_syllabics
from morphodict.paradigm.panes import RowLabel
from morphodict.orthography import ORTHOGRAPHY
from pytest_django.asserts import assertInHTML
from crkeng.app.preferences import DisplayMode

# Choose a tag whose label:
#  - probably won't change (or the tests will break)
#  - has at least one long vowel, so that we test that macrons are generated
TAGS = ("Sg",)
EXPECTED_LABEL_INTERNAL_ORTHOGRAPHY = "pêyak piko"


@pytest.mark.parametrize(
    ("orth", "expected"),
    [
        ("Latn", EXPECTED_LABEL_INTERNAL_ORTHOGRAPHY),
        ("Latn-x-macron", to_macrons(EXPECTED_LABEL_INTERNAL_ORTHOGRAPHY)),
        ("Cans", to_syllabics(EXPECTED_LABEL_INTERNAL_ORTHOGRAPHY)),
    ],
)
def test_relabel_respects_orthography(orth: str, expected: str) -> None:
    """
    Tests that relabelling for nêhiyawêwin respects the current orthography setting.
    """
    assert orth in ORTHOGRAPHY.available

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = "source_language"
    request.COOKIES[ORTHOGRAPHY.COOKIE_NAME] = orth

    context = RequestContext(request, {"label": RowLabel(TAGS)})
    template = Template("{% load relabelling %} {% relabel label.fst_tags %}")
    rendered = template.render(context)

    assertInHTML(expected, rendered)
