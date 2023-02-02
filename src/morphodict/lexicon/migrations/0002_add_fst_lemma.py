from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lexicon", "0001_initial_squashed"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="wordform",
            name="lexicon_wor_raw_ana_99bdb4_idx",
        ),
        migrations.RemoveIndex(
            model_name="wordform",
            name="lexicon_wor_text_f6cec4_idx",
        ),
        migrations.AddField(
            model_name="wordform",
            name="fst_lemma",
            field=models.CharField(
                help_text="\n            The form to use for generating wordforms of this lemma using the\n            generator FST. Should only be set for lemmas.\n         ",
                max_length=60,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="wordform",
            name="is_lemma",
            field=models.BooleanField(
                default=False, help_text="Whether this wordform is a lemma"
            ),
        ),
        migrations.AlterField(
            model_name="wordform",
            name="lemma",
            field=models.ForeignKey(
                help_text="The lemma of this wordform",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="inflections",
                to="lexicon.wordform",
            ),
        ),
        migrations.AlterField(
            model_name="wordform",
            name="paradigm",
            field=models.CharField(
                default=None,
                help_text="\n            If provided, this is the name of a paradigm that this wordform belongs\n            to. This name must match the filename or directory in res/layouts/\n            (without the file extension).\n        ",
                max_length=60,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="wordform",
            name="slug",
            field=models.CharField(
                help_text="\n            A stable unique identifier for a lemma. Used in public-facing URLs,\n            and for import reconciliation. It is recommended to use the wordform\n            text, optionally followed by ‘@’ and some sort of homograph\n            disambiguation string.\n        ",
                max_length=60,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddIndex(
            model_name="wordform",
            index=models.Index(
                fields=["text", "raw_analysis"], name="lexicon_wor_text_cc8d78_idx"
            ),
        ),
    ]
