from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0005_import_hash"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportStamp",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.FloatField(help_text="epoch time of import")),
            ],
        ),
    ]
