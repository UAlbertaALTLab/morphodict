import django
from django.test import TestCase, Client
from API.views import search

class SearchTest(TestCase):
    """Tests for the application views."""

    # Django requires an explicit setup() when running tests in PTVS
    @classmethod
    def setUpClass(cls):
        super(SearchTest, cls).setUpClass()
        django.setup()

    def test_connection(self):
        queryString = "mitas"
        response = self.client.get("/Search/" + queryString)
        self.assertEqual(response.status_code, 200)
