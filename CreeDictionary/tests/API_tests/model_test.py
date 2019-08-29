import random

from hypothesis import given
from hypothesis._strategies import composite, integers
from hypothesis.extra.django import from_model
import pytest
from API.models import Inflection


@pytest.fixture(scope="module")
def fff(request):
    print("123", vars(request.module))
    for i in range(random.randint(1, 20)):
        Inflection.objects.create(id=i).save()
    return 1


@composite
def shoot_inflections(draw):
    i = draw(integers())
    print("from shoot strategy:", Inflection.objects.all().count())
    return i


# @given(inflection=shoot_inflections())
def test_stuff(crk_eng_hundredth_file):
    a = 1
    pass
    # print("jj", lmaomlao)
    # print("yy", Inflection.objects.all().count())
    # print(inflection)
    assert 1 == 1


# @given(inflection=shoot_inflections())
# def test_new_stuff(stuff, inflection):
#     a = 1
#     print(inflection)
#     assert 1 == 1


@composite
def analyzable_db_lemmas(draw) -> Inflection:
    """
    lemmas with as_is being false
    """
    print(vars().items())
    pass
