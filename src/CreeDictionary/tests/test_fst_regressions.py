from morphodict.analysis import (
    RichAnalysis,
    rich_analyze_relaxed,
    strict_generator,
)


def test_fst_analysis():
    analyses = rich_analyze_relaxed("ta-pe-kiwemakaniyiw")
    assert (
        RichAnalysis((("PV/ta+", "PV/pe+"), "kîwêmakan", ("+V", "+II", "+Ind", "+4Sg")))
        in analyses
    )


def test_fst_generation():
    wordforms = set(strict_generator().lookup("PV/ta+PV/pe+kîwêmakan+V+II+Ind+4Sg"))
    assert "ta-pê-kîwêmakaniyiw" in wordforms
