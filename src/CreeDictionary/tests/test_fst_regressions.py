import pytest

from morphodict.analysis import RichAnalysis, rich_analyze_relaxed, strict_generator


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "ta-pe-kiwemakaniyiw",
            RichAnalysis(
                (("PV/ta+", "PV/pe+"), "kîwêmakan", ("+V", "+II", "+Ind", "+4Sg"))
            ),
        ),
        (
            # See: https://github.com/UAlbertaALTLab/morphodict/issues/897
            "ê-pim-nêhiyawêyahk",
            RichAnalysis(
                (("PV/e+", "PV/pimi+"), "nêhiyawêw", ("+V", "+AI", "+Cnj", "+12Pl"))
                # PV/e+PV/pimi+nêhiýawêw+V+AI+Cnj+12Pl
                # ê-pim-nêhiýawêyahk
            ),
        ),
        (
            # I have literally never heard anybody pronounce the "i-" in this word:
            "paskwâw-mostos",
            RichAnalysis(((), "paskwâwi-mostos", ("+N", "+A", "+Sg"))),
        ),
    ],
)
def test_fst_analysis(query: str, expected: RichAnalysis):
    analyses = rich_analyze_relaxed(query)
    assert expected in analyses


def test_fst_generation():
    wordforms = set(strict_generator().lookup("PV/ta+PV/pe+kîwêmakan+V+II+Ind+4Sg"))
    assert "ta-pê-kîwêmakaniyiw" in wordforms
