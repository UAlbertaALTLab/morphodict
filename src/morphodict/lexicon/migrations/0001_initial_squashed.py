from django.db import migrations, models
import django.db.models.deletion
import morphodict.lexicon.models


class Migration(migrations.Migration):
    replaces = [
        ("lexicon", "0001_initial"),
        ("lexicon", "0002_alter_wordform_linguist_info"),
        ("lexicon", "0003_remove_unused_dictionarysource_fields"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DictionarySource",
            fields=[
                (
                    "abbrv",
                    models.CharField(max_length=8, primary_key=True, serialize=False),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="What is the primary title of the dictionary source?",
                        max_length=256,
                    ),
                ),
                (
                    "author",
                    models.CharField(
                        blank=True,
                        help_text="Separate multiple authors with commas. See also: editor",
                        max_length=512,
                    ),
                ),
                (
                    "editor",
                    models.CharField(
                        blank=True,
                        help_text="Who edited or compiled this volume? Separate multiple editors with commas.",
                        max_length=512,
                    ),
                ),
                (
                    "year",
                    models.IntegerField(
                        blank=True,
                        help_text="What year was this dictionary published?",
                        null=True,
                    ),
                ),
                (
                    "publisher",
                    models.CharField(
                        blank=True, help_text="What was the publisher?", max_length=128
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True,
                        help_text="What is the city of the publisher?",
                        max_length=64,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Wordform",
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
                ("text", models.CharField(max_length=60)),
                (
                    "raw_analysis",
                    models.JSONField(
                        encoder=morphodict.lexicon.models.DiacriticPreservingJsonEncoder,
                        null=True,
                    ),
                ),
                (
                    "paradigm",
                    models.CharField(
                        default=None,
                        help_text="If provided, this is the name of a static paradigm that this wordform belongs to. This name should match the filename in res/layouts/static/ WITHOUT the file extension.",
                        max_length=60,
                        null=True,
                    ),
                ),
                (
                    "is_lemma",
                    models.BooleanField(
                        default=False,
                        help_text="The wordform is chosen as lemma. This field defaults to true if according to fst the wordform is not analyzable or it's ambiguous",
                    ),
                ),
                (
                    "slug",
                    models.CharField(
                        help_text="\n            A stable unique identifier for a lemma. Used in public-facing URLs,\n            and for import reconciliation.\n        ",
                        max_length=60,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "linguist_info",
                    models.JSONField(
                        blank=True,
                        help_text="\n            Various pieces of information about wordforms/lemmas that are of\n            interest to linguists, and are available for display in templates,\n            but that are not used by any of the logic in the morphodict code.\n        ",
                    ),
                ),
                (
                    "lemma",
                    models.ForeignKey(
                        help_text="The identified lemma of this wordform. Defaults to self",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inflections",
                        to="lexicon.wordform",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TargetLanguageKeyword",
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
                ("text", models.CharField(max_length=60)),
                (
                    "wordform",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="target_language_keyword",
                        to="lexicon.wordform",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SourceLanguageKeyword",
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
                ("text", models.CharField(max_length=60)),
                (
                    "wordform",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lexicon.wordform",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Definition",
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
                ("text", models.CharField(max_length=200)),
                (
                    "auto_translation_source",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="lexicon.definition",
                    ),
                ),
                ("citations", models.ManyToManyField(to="lexicon.DictionarySource")),
                (
                    "wordform",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="definitions",
                        to="lexicon.wordform",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="wordform",
            index=models.Index(
                fields=["raw_analysis"], name="lexicon_wor_raw_ana_99bdb4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="wordform",
            index=models.Index(fields=["text"], name="lexicon_wor_text_f6cec4_idx"),
        ),
        migrations.AddIndex(
            model_name="wordform",
            index=models.Index(
                fields=["is_lemma", "text"], name="lexicon_wor_is_lemm_916282_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="targetlanguagekeyword",
            index=models.Index(fields=["text"], name="lexicon_tar_text_69f04a_idx"),
        ),
        migrations.AddIndex(
            model_name="sourcelanguagekeyword",
            index=models.Index(fields=["text"], name="lexicon_sou_text_d9d495_idx"),
        ),
        migrations.AlterField(
            model_name="wordform",
            name="linguist_info",
            field=models.JSONField(
                blank=True,
                help_text="\n            Various pieces of information about wordforms/lemmas that are of\n            interest to linguists, and are available for display in templates,\n            but that are not used by any of the logic in the morphodict code.\n        ",
                null=True,
            ),
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="author",
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="city",
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="editor",
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="publisher",
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="title",
        ),
        migrations.RemoveField(
            model_name="dictionarysource",
            name="year",
        ),
    ]
