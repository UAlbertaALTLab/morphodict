from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lexicon", "0002_alter_wordform_linguist_info"),
    ]

    operations = [
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
