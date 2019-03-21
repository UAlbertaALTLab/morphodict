import django
from django.test import TestCase, Client
from API.views import displayWord
from urllib.parse import quote

class DisplayWordTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(DisplayWordTest, cls).setUpClass()
        django.setup()
        cls.client = Client()

    def test_connection(self):
        queryString = quote("mitâs")
        url = "/DisplayWord/" + queryString
        print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

