"""
Stub for data migration that used to add data to a table that no longer exists.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("API", "0005_wordform_paradigm"),
        ("CreeDictionary", "0002_change_example_site_to_cree_dictionary_site"),
    ]

    operations: list[migrations.RunPython] = []
