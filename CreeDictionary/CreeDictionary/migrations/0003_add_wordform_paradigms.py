from django.db import migrations

WORDFORM_TO_PARADIGM = {
    # Personal pronouns
    ("niya", "PRON"): "personal-pronouns",
    ("kiya", "PRON"): "personal-pronouns",
    ("wiya", "PRON"): "personal-pronouns",
    ("niyanân", "PRON"): "personal-pronouns",
    ("kiyânaw", "PRON"): "personal-pronouns",
    ("kiyawâw", "PRON"): "personal-pronouns",
    ("wiyawâw", "PRON"): "personal-pronouns",
    # Animate demonstratives
    ("awa", "PRON"): "demonstrative-pronouns",
    ("ana", "PRON"): "demonstrative-pronouns",
    ("nâha", "PRON"): "demonstrative-pronouns",
    ("ôki", "PRON"): "demonstrative-pronouns",
    ("aniki", "PRON"): "demonstrative-pronouns",
    ("nêki", "PRON"): "demonstrative-pronouns",
    # Inanimate demonstratives
    ("ôma", "PRON"): "demonstrative-pronouns",
    ("ôhi", "PRON"): "demonstrative-pronouns",
    ("anima", "PRON"): "demonstrative-pronouns",
    ("anihi", "PRON"): "demonstrative-pronouns",
    ("nêma", "PRON"): "demonstrative-pronouns",
    ("nêhi", "PRON"): "demonstrative-pronouns",
    # Inanimate/Obviative inanimate demonstratives
    ("ôhi", "PRON"): "demonstrative-pronouns",
    ("anihi", "PRON"): "demonstrative-pronouns",
    ("nêhi", "PRON"): "demonstrative-pronouns",
}


def add_explicit_paradigm_field(apps, schema_editor):
    """
    For the current (2021-05-07) paradigms, explicitly adds the paradigm filed.
    """
    Wordform = apps.get_model("API", "Wordform")

    objects_to_update = []

    for (text, pos), paradigm in WORDFORM_TO_PARADIGM.items():
        for wordform in Wordform.objects.filter(text=text, pos=pos):
            if wordform.paradigm:
                print(
                    "Not replacing existing paradigm on", wordform,
                    wordform.paradigm
                )
                continue
            wordform.paradigm = paradigm
            objects_to_update.append(wordform)

    Wordform.objects.bulk_update(objects_to_update, ["paradigm"])


class Migration(migrations.Migration):

    dependencies = [
        # Absolutely required by this migration:
        ("API", "0005_wordform_paradigm"),
        # Run this migration **after** this one:
        ("CreeDictionary", "0002_change_example_site_to_cree_dictionary_site"),
    ]

    operations = [migrations.RunPython(add_explicit_paradigm_field)]
