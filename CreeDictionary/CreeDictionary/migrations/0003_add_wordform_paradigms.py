from django.db import migrations

from CreeDictionary.CreeDictionary.ensure_data import (
    set_paradigm_for_demonstrative_and_personal_pronouns,
)


def add_explicit_paradigm_field(apps, schema_editor):
    """
    For the current (2021-05-07) paradigms, explicitly adds the paradigm filed.
    """
    Wordform = apps.get_model("API", "Wordform")
    to_update = set_paradigm_for_demonstrative_and_personal_pronouns(
        Wordform.objects.all()
    )
    Wordform.objects.bulk_update(to_update, ["paradigm"])


class Migration(migrations.Migration):

    dependencies = [
        # Absolutely required by this migration:
        ("API", "0005_wordform_paradigm"),
        # Run this migration **after** this one:
        ("CreeDictionary", "0002_change_example_site_to_cree_dictionary_site"),
    ]

    operations = [migrations.RunPython(add_explicit_paradigm_field)]
