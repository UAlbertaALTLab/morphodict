from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wordform",
            name="linguist_info",
            field=models.JSONField(
                blank=True,
                help_text="\n            Various pieces of information about wordforms/lemmas that are of\n            interest to linguists, and are available for display in templates,\n            but that are not used by any of the logic in the morphodict code.\n        ",
                null=True,
            ),
        ),
    ]
