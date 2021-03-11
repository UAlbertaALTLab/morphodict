"""
Inserts bibliographic information for three Plains Cree dictionary sources:
    - [CW] Cree : Words - edited by Arok Wolvengrey
    - [MD] Maskwacîs Dictionary
    - [AE] Alberta Elders' Cree Dictionary
"""
from django.db import migrations

BIBLIOGRAPHY = {
    "MD": {
        "title": "Maskwacîs Dictionary of Cree Words / Nehiyaw Pîkiskweninisa",
        "editor": "Maskwaschees Cultural College",
        "publisher": "Maskwachees Cultural College",
        "year": 2009,
        "city": "Maskwacîs, Alberta",
    },
    "CW": {
        "title": "nêhiyawêwin : itwêwina / Cree : Words",
        "editor": "Arok Wolvengrey",
        "year": 2001,
        "publisher": "Canadian Plains Research Center",
        "city": "Regina, Saskatchewan",
    },
    "AE": {
        "title": "Alberta Elders' Cree Dictionary/"
        "alperta ohci kehtehayak nehiyaw otwestamâkewasinahikan",
        "author": "Nancy LeClaire, George Cardinal",
        "editor": "Earle H. Waugh",
        "year": 2002,
        "publisher": "The University of Alberta Press",
        "city": "Edmonton, Alberta",
    },
}


def insert_bibliographic_information(apps, schema_editor):
    DictionarySource = apps.get_model("API", "DictionarySource")

    for abbrv, fields in BIBLIOGRAPHY.items():
        source, created = DictionarySource.objects.get_or_create(abbrv=abbrv)
        if source.title or source.author or source.editor:
            # Already has data -- Skip!
            continue

        for attr, data in fields.items():
            setattr(source, attr, data)
        source.save()


class Migration(migrations.Migration):
    dependencies = [
        ("API", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(insert_bibliographic_information),
    ]
