"""
The Django "sites" framework is annoying because it automatically creates a site called
"example.com" instead of... you know... the name of the current site AS A POST-MIGRATION
HOOK!

This means the "example" _might_ be in the database. Or it might not.

Regardless, this migration changes it to the site configured in settings.py.
"""

from django.conf import settings
from django.db import migrations


def change_example_to_production_site(apps, schema_editor):
    """
    Changes the example.com site to the current site domain.
    As of 2021-03-11, this is itwewina.altlab.app.
    """
    Site = apps.get_model("sites", "Site")
    site, created = Site.objects.get_or_create(pk=1)

    if not created:
        # See: https://github.com/django/django/blob/876dc0c1a7dbf569782eb64f62f339c1daeb75e0/django/contrib/sites/management.py#L11-L38
        assert site.name == "example.com"
        print("overwriting the default site")

    site.name = site.domain = settings.PRODUCTION_HOST
    site.save()


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("CreeDictionary", "0001_insert_bibliographic_data"),
    ]

    operations = [migrations.RunPython(change_example_to_production_site)]
