# Written by Matt 2.2.11 on 2020-03-25 02:16

from django.db import migrations, models
from utils.cree_lev_dist import remove_cree_diacritics


def fill_in_ascii_text_field(apps, schema_editor):
    Wordform = apps.get_model("API", "Wordform")
    wordforms = Wordform.objects.all()
    for wf in wordforms:
        wf.ascii_text = remove_cree_diacritics(wf.text)
    Wordform.objects.bulk_update(wordforms, ["ascii_text"])


def clear_ascii_text_field(apps, schema_editor):
    Wordform = apps.get_model("API", "Wordform")
    wordforms = Wordform.objects.all()
    for wf in wordforms:
        wf.ascii_text = ""
    Wordform.objects.bulk_update(wordforms, ["ascii_text"])


class Migration(migrations.Migration):

    dependencies = [
        ("API", "0008_auto_20200221_0220"),
    ]

    operations = [
        migrations.AddField(
            model_name="wordform",
            name="ascii_text",
            field=models.CharField(default="", max_length=40),
            preserve_default=False,
        ),
        migrations.RunPython(
            fill_in_ascii_text_field, reverse_code=clear_ascii_text_field
        ),
    ]
