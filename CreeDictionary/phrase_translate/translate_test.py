import pytest

from API.models import Wordform
from phrase_translate.translate import inflect_english_phrase


@pytest.mark.django_db
def test_translate_star() -> None:
    star = Wordform.objects.get(text="acâhkosa", lemma__text="atâhk")
    assert inflect_english_phrase(star.analysis, "star") == "little star over there"


def test_in_my_little_book():
    assert (
        inflect_english_phrase("masinahikan+N+Dim+Px1Sg+Loc", "book")
        == "in my little book"
    )


@pytest.mark.django_db
def test_translate_in_my_little_cree_book():
    wordform = Wordform.objects.get(
        text="ninêhiyawasinahikanisihk", lemma__text="nêhiyawasinahikan"
    )
    print(wordform.analysis)
    assert (
        inflect_english_phrase(wordform.analysis, "Cree book")
        == "in my little Cree book"
    )
