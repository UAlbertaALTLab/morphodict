from constants import Analysis
from shared import DescriptiveAnalyzer, NormativeGenerator


def test_descriptive_analyzer_single_invocation():
    analyzer = DescriptiveAnalyzer()

    result = analyzer.analyze("wapamat")
    assert {
        "wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO",
        "wâpamêw+V+TA+Cnj+Prs+2Sg+3SgO",
    } == result


def test_descriptive_analyzer_multiple_invocation():
    analyzer = DescriptiveAnalyzer()

    result_1 = analyzer.analyze("wapamat")
    assert {
        "wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO",
        "wâpamêw+V+TA+Cnj+Prs+2Sg+3SgO",
    } == result_1

    new_analyzer = DescriptiveAnalyzer()
    # test singleton class
    assert id(new_analyzer) == id(analyzer)

    # assert that the effects does not vary
    assert new_analyzer.analyze("wapamat") == result_1


def test_normative_generator_single_invocation():
    generator = NormativeGenerator()

    result = generator.generate(Analysis("wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO"))
    assert {"wâpamât"} == result


def test_normative_generator_multiple_invocation():
    generator = NormativeGenerator()

    result_1 = generator.generate(Analysis("wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO"))
    assert {"wâpamât"} == result_1

    new_generator = NormativeGenerator()
    # test singleton class
    assert id(new_generator) == id(generator)

    # assert that the effects does not vary
    assert (
        new_generator.generate(Analysis("wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO")) == result_1
    )
