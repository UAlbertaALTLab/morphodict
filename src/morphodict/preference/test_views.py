import secrets

import pytest
from django.http import Http404
from django.test import RequestFactory

from morphodict.preference import register_preference, Preference, registry
from morphodict.preference.views import change_preference


def test_post_preference(rf: RequestFactory, pet_preference: Preference):
    """
    Tests the happy path for setting a preference.
    """
    name = pet_preference.cookie_name
    choice = "dogs"

    request = rf.post(f"/change-preference/{name}", data={name: choice})
    response = change_preference(request, name)

    assert response.cookies[name].value == choice


def test_bad_choice(rf: RequestFactory, pet_preference: Preference):
    """
    Tests the happy path for setting a preference.
    """
    name = pet_preference.cookie_name
    choice = arbitrary_string()

    assert choice not in pet_preference.choices

    request = rf.post(f"/change-preference/{name}", data={name: choice})
    response = change_preference(request, name)

    # It should be a bad request of some sort:
    assert response.status_code in range(400, 500)
    assert name not in response.cookies


def test_preference_unknown(rf: RequestFactory):
    unknown_name = arbitrary_string()
    choice = arbitrary_string()

    assert unknown_name not in registry()

    request = rf.post(f"/change-preference/{unknown_name}", data={unknown_name: choice})

    with pytest.raises(Http404):
        change_preference(request, unknown_name)


@pytest.fixture(scope="session")
def pet_preference() -> Preference:
    @register_preference
    class Pet(Preference):
        default = "cats"
        cookie_name = "pet"
        choices = {"cats": "Cats", "dogs": "Dogs"}

    return registry()[Pet.name]


def arbitrary_string() -> str:
    """
    :return: an arbitrary, URL-safe string.
    """
    return secrets.token_urlsafe()
