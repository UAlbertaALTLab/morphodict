import sys
from os import path

import django
import os

sys.path.append(path.join(path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CreeDictionary.settings'
django.setup()

from API.models import Word
