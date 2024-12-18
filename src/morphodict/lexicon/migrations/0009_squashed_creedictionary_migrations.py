# Generated by Django 4.2.16 on 2024-10-18 18:34

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def change_example_to_production_site(apps, schema_editor):
    """
    Changes the example.com site to the current site domain.
    As of 2021-03-11, this is itwewina.altlab.app.
    """
    Site = apps.get_model("sites", "Site")
    site, created = Site.objects.get_or_create(pk=1)

    if not created:
        # See: https://github.com/django/django/blob/876dc0c1a7dbf569782eb64f62f339c1daeb75e0/django/contrib/sites/management.py#L11-L38
        print(
            f"overwriting the site {site.domain} (displayed {site.name}) with new site {settings.PRODUCTION_HOST}"
        )

    site.name = site.domain = settings.PRODUCTION_HOST
    site.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("lexicon", "0008_add_semantic_fields"),
    ]

    operations = [
        migrations.RunPython(
            code=change_example_to_production_site,
        ),
    ]
