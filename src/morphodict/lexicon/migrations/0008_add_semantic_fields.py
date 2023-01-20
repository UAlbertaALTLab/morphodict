# Generated by Django 3.2.15 on 2023-01-20 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0007_merge_20211001_1712"),
    ]

    operations = [
        migrations.AddField(
            model_name="wordform",
            name="rw_domains",
            field=models.CharField(
                blank=True,
                help_text="\n            RapidWords domains for an entry, separated by a semicolon\n            ",
                max_length=2048,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="wordform",
            name="rw_indices",
            field=models.CharField(
                blank=True,
                help_text="\n                RapidWords indices for an entry, separated by a semicolon\n                ",
                max_length=2048,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="wordform",
            name="wn_synsets",
            field=models.CharField(
                blank=True,
                help_text="\n                WordNet synsets for an entry, separated by a semicolon\n                ",
                max_length=2048,
                null=True,
            ),
        ),
    ]
