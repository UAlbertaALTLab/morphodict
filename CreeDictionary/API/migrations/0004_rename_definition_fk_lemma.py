# Created by Matt Yan 2019-12-22
# to fix #181 https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/181
# allow inflected wordforms to have lemmas

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("API", "0003_auto_20191125_2357")]

    operations = [
        migrations.RenameField(
            model_name="Definition", old_name="lemma", new_name="wordform"
        )
    ]
