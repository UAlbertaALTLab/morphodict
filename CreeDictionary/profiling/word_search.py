import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()

from API.models import Inflection

q = Inflection.fetch_lemmas_by_user_query("explain")
