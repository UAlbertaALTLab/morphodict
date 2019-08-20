import pytest

from DatabaseManager.cree_inflection_generator import expand_inflections
from DatabaseManager.xml_importer import clear_database, import_crkeng_xml
from utils.crkeng_xml_utils import get_xml_lemma_set

# todo: this
# @pytest.mark.django_db
# def test_import_xml(shared_datadir):
#     lemma_set = get_xml_lemma_set(shared_datadir / "crkeng-small.xml")
#     print(lemma_set)
#     # import_crkeng_xml(
#     #     shared_datadir / "crkeng-small.xml", multi_processing=1, verbose=False
#     # )
#
#     expanded = expand_inflections(lemma_set)
#     for analysis, inflections in expanded.values():
#         print(analysis)


#
# @pytest.mark.django_db
# def test_clear_database():
#     clear_database(verbose=False)
