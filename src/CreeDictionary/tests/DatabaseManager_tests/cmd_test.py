import pytest
from django.core.management import call_command

from CreeDictionary.API.models import Wordform
from CreeDictionary.DatabaseManager.cree_inflection_generator import expand_inflections
from CreeDictionary.DatabaseManager.xml_importer import import_xmls


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    call_command("migrate", "API")
    import_xmls(shared_datadir / "crkeng-small-nice-0")

    expanded = expand_inflections(["yôwamêw+V+TA+Ind+3Sg+4Sg/PlO"], verbose=False)
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1
