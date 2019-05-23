import django
from django.test import TestCase, Client
from django.urls import reverse

from API.views import search
from API.models import *
import json


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Lemma.objects.create(id=1, context="mitâs", language="crk", type="N")
        Lemma.objects.create(id=2, context="picikwâs", language="crk", type="N")
        Definition.objects.create(id=1, fk_word_id=2, source="CW", context="apple")

    @classmethod
    def setUpClass(cls):
        super(SearchTest, cls).setUpClass()
        django.setup()

    def test_connection(self):
        queryString = "mitâs"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)

    def test_misspell(self):
        queryString = "mitas"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)

    def test_partial(self):
        queryString = "tâ"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)

    def test_not_found(self):
        queryString = "ABCDEFGHIJKLMN"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 0)

    def test_english_definition(self):
        queryString = "apple"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)
        self.assertEqual(content["words"][0]["context"], "picikwâs")

    def test_english_definition_case_sensitivity(self):
        queryString = "APPlE"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content["words"]), 1)
        self.assertEqual(content["words"][0]["context"], "picikwâs")

    def test_cree_linguistic_analysis(self):
        queryString = "mitas"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertGreaterEqual(len(content["analysis"]), 1)

    def test_english_linguistic_analysis(self):
        queryString = "apple"
        response = self.client.get(
            reverse("cree-dictionary-search-api", args=(queryString,))
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertFalse("analysis" in content)
