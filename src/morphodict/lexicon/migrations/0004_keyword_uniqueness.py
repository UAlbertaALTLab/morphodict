from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lexicon", "0003_populate_fst_lemma"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="sourcelanguagekeyword",
            constraint=models.UniqueConstraint(
                fields=("text", "wordform_id"), name="source_kw_text_and_wordform"
            ),
        ),
        migrations.AddConstraint(
            model_name="targetlanguagekeyword",
            constraint=models.UniqueConstraint(
                fields=("text", "wordform_id"), name="target_kw_text_and_wordform"
            ),
        ),
    ]
