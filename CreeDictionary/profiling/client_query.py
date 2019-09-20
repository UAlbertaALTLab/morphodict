import os
import django
from django.test import Client

os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()

if __name__ == "__main__":
    c = Client()

    c.get("/cree-dictionary/search/miteh")
