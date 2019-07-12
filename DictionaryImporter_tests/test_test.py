import os
import sys
from os import path

import django

FILE_DIR = path.dirname(__file__)
sys.path.extend(path.join(FILE_DIR, '..', 'CreeDictionary'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'CreeDictionary.CreeDictionary.settings'
django.setup()
# from CreeDictionary.API.models import Word
