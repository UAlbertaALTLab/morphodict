import logging

import pytest

from API.models import Inflection
from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import clear_database, import_crkeng_xml
from utils.crkeng_xml_utils import get_xml_lemma_set


@pytest.mark.django_db
def test_import_xml(shared_datadir):
    import_crkeng_xml(
        shared_datadir / "crkeng-small.xml", multi_processing=1, verbose=False
    )

    expanded = expand_inflections(
        ["yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"], multi_processing=1, verbose=False
    )
    for analysis_and_inflections in expanded.values():
        for analysis, inflections in analysis_and_inflections:
            for inflection in inflections:
                assert len(Inflection.objects.filter(text=inflection)) >= 1


#
# @pytest.mark.django_db
# def test_clear_database():
#     clear_database(verbose=False)
