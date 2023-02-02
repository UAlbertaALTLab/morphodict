from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lexicon", "0004_keyword_uniqueness"),
    ]

    operations = [
        migrations.AddField(
            model_name="wordform",
            name="import_hash",
            field=models.CharField(
                help_text="\n            A hash of the input JSON, used to determine whether to update an\n            entry or not. Only valid on lemmas.\n        ",
                max_length=60,
                null=True,
            ),
        ),
    ]
