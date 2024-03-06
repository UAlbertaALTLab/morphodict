"""
Stub for data migration that used to add data to a table that no longer exists.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("API", "0001_initial"),
    ]

    operations: list[migrations.RunPython] = []
