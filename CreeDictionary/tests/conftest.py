from os.path import dirname
from pathlib import Path

import pytest
import xml_subsetter
from django.db import transaction
from hypothesis import assume
from hypothesis._strategies import composite, integers

from API.models import Inflection
from DatabaseManager.xml_importer import import_crkeng_xml
from constants import LexicalCategory
from utils import shared_res_dir, hfstol_analysis_parser


@pytest.fixture(scope="session")
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


@composite
def random_inflections(draw) -> Inflection:
    """
    hypothesis strategy to supply random inflections
    """
    inflection_objects = Inflection.objects.all()
    id = draw(integers(min_value=1, max_value=inflection_objects.count()))
    return inflection_objects.get(id=id)


@composite
def analyzable_inflections(draw) -> Inflection:
    """
    inflections with as_is field being False, meaning they have an analysis field from fst analyzer
    """
    inflection_objects = Inflection.objects.all()

    pk_id = draw(integers(min_value=1, max_value=inflection_objects.count()))
    the_inflection = inflection_objects.get(id=pk_id)
    assume(not the_inflection.as_is)
    return the_inflection


@composite
def inflections_of_category(draw, lc: LexicalCategory) -> Inflection:
    """
    hypothesis strategy to supply random inflections
    """
    inflection = draw(random_inflections())
    assume(not inflection.as_is)
    assume(hfstol_analysis_parser.extract_category(inflection.analysis) is lc)
    return inflection


@pytest.fixture(scope="session")
def crk_eng_hundredth_file(topmost_datadir) -> Path:
    """
    1/100 of the entries in the real crkeng.xml
    """

    hundredths_file = Path(topmost_datadir) / "crkeng_hundredth.xml"

    def create_crkeng_hundredth():
        """
        create the file if it does not already exist
        """
        crkeng_file = shared_res_dir / "dictionaries" / "crkeng.xml"
        if not crkeng_file.exists():
            raise FileNotFoundError("%s not found" % crkeng_file)
        xml_subsetter.subset_head(crkeng_file, hundredths_file, "e", 0.01)

    if not hundredths_file.exists():
        create_crkeng_hundredth()

    return hundredths_file
