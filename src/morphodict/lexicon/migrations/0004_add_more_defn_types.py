from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0003_populate_fst_lemma"),
    ]

    operations = [
        migrations.AddField(
            model_name="definition",
            name="raw_core_definition",
            field=models.CharField(
                help_text="\n            The definition to optionally use for auto-translation.\n\n            It should include only the core sense of the wordform without any\n            notes or cross-references.\n        ",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="definition",
            name="raw_semantic_definition",
            field=models.CharField(
                help_text="\n            The definition to optionally use when building a semantic vector.\n\n            This is not visible to the user. It may include etymological terms,\n            and may omit stopwords.\n\n            Even though it is only used at import time, it is stored in the\n            database to enable the possibility of regenerating definition\n            vectors without the original importjson file.\n        ",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="definition",
            name="text",
            field=models.CharField(
                help_text="\n            The definition text. This is displayed to the user, and terms within\n            it are indexed for full-text search.\n        ",
                max_length=200,
            ),
        ),
    ]
