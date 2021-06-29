import pytest

from CreeDictionary.CreeDictionary.management.commands.dumpimportjson import (
    slug_disambiguator,
)


@pytest.mark.parametrize(
    ("input_things", "expected_outputs"),
    [
        [["XYZ"], [""]],
        [["V", "N", "N"], ["@v", "@n.1", "@n.2"]],
        [["PR", "VTI"], ["@p", "@v"]],
        [["PR", "PrA"], ["@pr", "@pra"]],
        [["PrA", "PrI"], ["@pra", "@pri"]],
        [["NA", "VTI"], ["@n", "@v"]],
        [["NA", "VAI", "VTI"], ["@n", "@vai", "@vti"]],
        [["NA", "NI"], ["@na", "@ni"]],
        [["NA", "NA"], ["@na.1", "@na.2"]],
        [["NA-1", "NA-2"], ["@na-1", "@na-2"]],
        [["VTI", "NA-1", "NA-2"], ["@v", "@na-1", "@na-2"]],
    ],
)
def test_slug_creator(input_things, expected_outputs):
    assert slug_disambiguator(input_things) == expected_outputs
