from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("API", "0005_wordform_paradigm"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="englishkeyword",
            name="lemma",
        ),
        migrations.RemoveField(
            model_name="wordform",
            name="lemma",
        ),
        migrations.DeleteModel(
            name="Definition",
        ),
        migrations.DeleteModel(
            name="DictionarySource",
        ),
        migrations.DeleteModel(
            name="EnglishKeyword",
        ),
        migrations.DeleteModel(
            name="Wordform",
        ),
    ]
