import pytest

from API.models import Wordform
from DatabaseManager.__main__ import import_and_migrate


@pytest.mark.django_db
def test_import_xml_common_analysis_definition_merge(shared_datadir):
    import_and_migrate(
        shared_datadir / "crkeng-regression-0", process_count=1, no_input=True
    )

    query_set = Wordform.objects.filter(text="nipa")

    kill_him_inflections = []
    for inflection in query_set:
        for definition in inflection.definitions.all():
            if "Kill" in definition.text:
                kill_him_inflections.append(inflection)

    assert len(kill_him_inflections) == 1
    kill_him_inflection = kill_him_inflections[0]
    assert kill_him_inflection.pos == "V"
