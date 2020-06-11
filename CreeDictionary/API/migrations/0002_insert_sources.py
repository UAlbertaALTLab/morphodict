from django.db import migrations


def sources_to_citations(apps, schema_editor):
    """
    From the sources field, creates citations.
    """
    Definition = apps.get_model("API", "Definition")
    DictionarySource = apps.get_model("API", "DictionarySource")

    # Create the two initial sources:
    sources = {
        "MD": DictionarySource(
            abbrv="MD",
            title="Maskwacîs Dictionary of Cree Words / Nehiyaw Pîkiskweninisa",
            editor="Maskwachees Cultural College",
            year=2009,
            city="Maskwacîs, Alberta",
        ),
        "CW": DictionarySource(
            abbrv="CW",
            title="nêhiyawêwin : itwêwina / Cree : Words",
            editor="Arok Wolvengrey",
            year=2001,
            publisher="Canadian Plains Research Center",
            city="Regina, Saskatchewan",
        ),
    }
    for src in sources.values():
        src.save()

    # Convert the sources (stored as a string) to citations:
    for dfn in Definition.objects.all():
        source_ids = sorted(source.abbrv for source in dfn.citations.all())
        for source_id in source_ids:
            assert source_id in sources
            dfn.citations.add(source_id)
        dfn.save()


class Migration(migrations.Migration):
    dependencies = [("API", "0001_initial")]

    operations = [migrations.RunPython(sources_to_citations)]
