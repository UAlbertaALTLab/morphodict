import pytest
from django.urls import reverse

from CreeDictionary.API.models import Wordform


@pytest.mark.django_db
def test_admin_doesnt_crash(admin_client):
    "This is a minimal test that we can view a wordform in the admin interface"
    one_wordform = Wordform.objects.filter(is_lemma=True).first()
    response = admin_client.get(
        reverse("admin:API_wordform_change", args=[one_wordform.id])
    )
    assert response.status_code == 200
    assert b"Inflections" in response.content
