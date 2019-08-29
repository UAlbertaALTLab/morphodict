from os.path import dirname
from pathlib import Path

import pytest
import xml_subsetter

from utils import shared_res_dir


@pytest.fixture
def topmost_datadir():
    return Path(dirname(__file__)) / "data"


@pytest.fixture
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
