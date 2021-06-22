import pytest

from CreeDictionary.CreeDictionary.management.commands.dumpimportjson import (
    slug_disambiguator,
)


@pytest.mark.parametrize(
    ("input_things", "expected_outputs"),
    [
        [["XYZ"], [""]],
        [["NA", "VTI"], ["@N", "@V"]],
        [["NA", "NI"], ["@NA", "@NI"]],
        [["NA", "NA"], ["@1", "@2"]],
        [["NA-1", "NA-2"], ["@NA-1", "@NA-2"]],
        [["VTI", "NA-1", "NA-2"], ["@V", "@NA-1", "@NA-2"]],
    ],
)
def test_slug_creator(input_things, expected_outputs):
    assert slug_disambiguator(input_things) == expected_outputs
