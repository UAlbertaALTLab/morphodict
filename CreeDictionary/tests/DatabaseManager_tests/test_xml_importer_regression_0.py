import pytest

from API.models import Wordform
from tests.conftest import migrate_and_import


@pytest.mark.django_db
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    migrate_and_import(shared_datadir / "crkeng-regression-0")

    query_set = Wordform.objects.filter(text="nipa")

    kill_him_inflections = []
    for inflection in query_set:
        for definition in inflection.definitions.all():
            if "Kill" in definition.text:
                kill_him_inflections.append(inflection)

    assert len(kill_him_inflections) == 1
    kill_him_inflection = kill_him_inflections[0]
    assert kill_him_inflection.pos == "V"
