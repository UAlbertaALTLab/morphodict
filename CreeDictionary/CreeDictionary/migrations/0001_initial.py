"""
The Django "sites" framework is annoying because it automatically creates a site called
"example.com" instead of... you know... the name of the current site.

This migration changes it to the site configured in settings.py.
"""

from django.conf import settings
from django.db import migrations


def change_example_to_production_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    site = Site.objects.get(pk=1)
    site.name = site.domain = settings.PRODUCTION_HOST
    site.save()


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [migrations.RunPython(change_example_to_production_site)]
