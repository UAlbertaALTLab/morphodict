import django
from django.test import TestCase, Client
from API.views import displayWord
from API.models import *
from urllib.parse import quote
import json


class DisplayWordTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Lemma.objects.create(id=1, context="mitâs", language="crk", type="N")
        Definition.objects.create(id=1, fk_word_id=1, source="CW", context="Pants.")
        Inflection.objects.create(id=2, fk_lemma_id=1, context="mitâsa", type="N", language="crk")
        InflectionForm.objects.create(id=1, fk_inflection_id=2, name="N")
        InflectionForm.objects.create(id=2, fk_inflection_id=2, name="A")

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

    def test_inflection(self):
        queryString = quote("mitâs")
        response = self.client.get("/DisplayWord/" + queryString)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue("lemma" in content)
        self.assertEqual(len(content["inflections"]), 1)
        self.assertEqual(len(content["inflections"][0]["inflectionForms"]), 2)
