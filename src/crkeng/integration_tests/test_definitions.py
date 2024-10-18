import pytest

from morphodict.search import search
from morphodict.conftest import django_db_setup
from morphodict.lexicon.models import Wordform, TargetLanguageKeyword

# This no-op keeps PyCharm for optimizing the required import away
django_db_setup


def first_definition_for(slug):
    wf = Wordform.objects.get(slug=slug)
    return wf.definitions.first()


def test_db_has_custom_fields(db):
    defn = first_definition_for("kwâskwêpayihôs")
    assert (
        defn.text
        == 'mule deer [literally: "jumper; leaper"; Lt: Odocoileus hemionus hemionus]'
    )
    assert (
        defn.semantic_definition
        == "mule deer jumper Odocoileus hemionus hemionus leaper"
    )
    assert defn.core_definition == "mule deer"

    assert set(
        r[0]
        for r in TargetLanguageKeyword.objects.filter(
            wordform=defn.wordform
        ).values_list("text")
    ) == {"odocoileus", "deer", "mule", "jumper", "hemionus", "leaper"}


@pytest.mark.parametrize("search_term", ["jumper", "Odocoileus"])
def test_extra_pieces_searchable(db, search_term):
    search_results = search(query=search_term).presentation_results()
    assert any(r.wordform.text == "kwâskwêpayihôs" for r in search_results)


def test_auto_translation_works(db):
    """
    This would fail if auto-translation tried to use the full definition
    """
    defn = Wordform.objects.get(text="nitâcimon").definitions.first()
    assert defn.text == "I tell, I tell a story"
    assert defn.auto_translation_source_id is not None


def test_object_has_default_values_for_extra_definition_types(db):
    """
    When an entry *doesn’t* have any special core_definition or semantic_definition.
    """
    defn = first_definition_for("maskwa@1")

    assert defn.text == "bear, black bear"
    assert defn.semantic_definition == "bear black bear"
    assert defn.core_definition == defn.text
