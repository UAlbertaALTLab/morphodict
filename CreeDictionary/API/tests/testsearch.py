import django
from django.test import TestCase, Client
from API.views import search
from API.models import *
import json

class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Lemma.objects.create(id=1, context="mitâs", language="crk", type="N")

    @classmethod
    def setUpClass(cls):
        super(SearchTest, cls).setUpClass()
        django.setup()

    def test_connection(self):
        queryString = "mitâs"
        response = self.client.get("/Search/" + queryString)
        self.assertEqual(response.status_code, 200)

    def test_misspell(self):
        queryString = "mitas"
        response = self.client.get("/Search/" + queryString)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)

    def test_partial(self):
        queryString = "tâ"
        response = self.client.get("/Search/" + queryString)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)

    def test_not_found(self):
        queryString = "ABCDEFGHIJKLMN"
        response = self.client.get("/Search/" + queryString)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 0)

