import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()

from API.models import Wordform

if __name__ == "__main__":
    Wordform.fetch_lemma_by_user_query("miteh")
