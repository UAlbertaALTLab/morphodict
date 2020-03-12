import pytest
from django.core.management import call_command

from API.models import Wordform
from DatabaseManager.__main__ import cmd_entry
from DatabaseManager.cree_inflection_generator import expand_inflections


@pytest.mark.django_db
def test_import_nice_xml(shared_datadir):
    call_command("migrate", "API", "0005")
    cmd_entry([..., "import", str(shared_datadir / "crkeng-small-nice-0")])

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Wordform.objects.filter(text=inflection)) >= 1
