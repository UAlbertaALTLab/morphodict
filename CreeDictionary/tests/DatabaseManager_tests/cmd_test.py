import pytest

from API.models import Inflection, Definition
from DatabaseManager.__main__ import cmd_entry
from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import import_crkeng_xml


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    cmd_entry([..., "import", str(shared_datadir / "crkeng-small-nice-0.xml")])

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Inflection.objects.filter(text=inflection)) >= 1


@pytest.mark.django_db
def test_clear_database(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small-nice-0.xml", multi_processing=1, verbose=False
    )
    assert Inflection.objects.all().count() != 0
    assert Definition.objects.all().count() != 0

    cmd_entry([..., "clear"])

    assert Inflection.objects.all().count() == 0
    assert Definition.objects.all().count() == 0
