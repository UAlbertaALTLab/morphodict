"""
Test Django template context processors.
"""

import pytest
from django.http import HttpRequest
from django.template import RequestContext, Template

from crkeng.app.preferences import DisplayMode


@pytest.fixture(autouse=True)
def ensure_context_processors_are_enabled(settings):
    desired_processor = (
        "morphodict.frontend.context_processors.display_options"
    )
    settings.TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": [desired_processor]},
        }
    ]


def test_render_with_display_mode_unset() -> None:
    request = HttpRequest()
    context = RequestContext(request, {})

    template = Template("{{ display_options.mode }}")
    assert template.render(context) == DisplayMode.default


@pytest.mark.parametrize("mode", DisplayMode.choices)
def test_use_display_mode(mode: str) -> None:
    """
    Render the request using a valid display mode.
    """
    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = mode
    context = RequestContext(request, {})

    template = Template("{{ display_options.mode }}")
    assert template.render(context) == mode


def test_set_bad_display_mode() -> None:
    """
    Render with a bad (invalid) display mode cookie.
    """
    bad_mode = "fhqwhgads"
    assert bad_mode not in DisplayMode.choices

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = bad_mode
    context = RequestContext(request, {})

    template = Template("{{ display_options.mode }}")
    assert template.render(context) != bad_mode
    assert template.render(context) == DisplayMode.default
