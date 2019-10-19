from os.path import dirname
from pathlib import Path

import pytest
import xml_subsetter
from django.db import transaction
from hypothesis import assume
from hypothesis._strategies import composite, integers, sampled_from

from API.models import Inflection
from DatabaseManager.xml_importer import import_xmls
from constants import LexicalCategory
from utils import shared_res_dir, hfstol_analysis_parser


@pytest.fixture(scope="session")
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


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
def random_inflections(draw) -> Inflection:
    """
    hypothesis strategy to supply random inflections
    """
    inflection_objects = Inflection.objects.all()
    id = draw(integers(min_value=1, max_value=inflection_objects.count()))
    return inflection_objects.get(id=id)


@composite
def random_lemmas(draw) -> Inflection:
    """
    Strategy that supplies wordforms that are also lemmas!
    """
    lemmas = list(Inflection.objects.filter(is_lemma=True, as_is=False))
    # Sometimes two different wordforms are marked as lemmas of the same word,
    # and yet they have different spelling. (Ed: that's not... what the word
    # "lemma" means, but okay...). So make sure to get the DEFAULT spelling
    # only!
    # e.g., akocin and akociniw are both two different spellings of the same
    # lemma.
    lemmas = [lemma for lemma in lemmas if lemma.default_spelling.id == lemma.id]
    return draw(sampled_from(lemmas))


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
def one_hundredth_xml_dir(topmost_datadir) -> Path:
    """
    1/100 of the entries in the real crkeng.xml
    """

    hundredth_dir = Path(topmost_datadir) / "one_hundredth_xmls"
    one_hundredth_crkeng = hundredth_dir / "crkeng.xml"
    one_hundredth_engcrk = hundredth_dir / "engcrk.xml"

    def create_hundredth_file(source: Path, target_file: Path):
        """
        create the file if it does not already exist
        """
        if not source.exists():
            raise FileNotFoundError("%s not found" % source)
        xml_subsetter.subset_head(source, target_file, "e", 0.01)

    if not one_hundredth_crkeng.exists():
        create_hundredth_file(
            shared_res_dir / "dictionaries" / "crkeng.xml", one_hundredth_crkeng
        )
    if not one_hundredth_engcrk.exists():
        create_hundredth_file(
            shared_res_dir / "dictionaries" / "engcrk.xml", one_hundredth_engcrk
        )

    return hundredth_dir
