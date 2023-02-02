from django.db import migrations
from django.db.migrations import RunPython


def populate_fst_lemma(apps, schema_editor):
    Wordform = apps.get_model("lexicon", "Wordform")
    for wf in Wordform.objects.filter(is_lemma=True):
        if wf.raw_analysis and wf.fst_lemma is None:
            wf.fst_lemma = wf.raw_analysis[1]
            wf.save()


def noop(apps, schema_editor):
    """Empty operation to allow this migration to be reversed

    When re-applying it, populate_fst_lemma will run again.
    """
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("lexicon", "0002_add_fst_lemma"),
    ]

    operations = [RunPython(populate_fst_lemma, noop)]
