# Generated by Django 3.2 on 2021-04-14 23:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("API", "0003_wordform_indexes"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="wordform",
            index=models.Index(fields=["is_lemma", "text"], name="lemma_text_idx"),
        ),
    ]
