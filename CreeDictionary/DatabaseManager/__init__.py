"""
meant to be used from command line to manage the database
"""
import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "CreeDictionary.settings"
django.setup()
