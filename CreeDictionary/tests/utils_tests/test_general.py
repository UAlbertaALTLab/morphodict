"""
separate test files need to be created for the tests in this file.
todo: delete this file
"""
import xml.etree.ElementTree as ET

import pytest

from constants import LexicalCategory
from utils import extract_category, identify_lemma_analysis
from utils import fst_analysis_parser
from utils.crkeng_xml_utils import extract_l_str


@pytest.mark.parametrize(
    "analysis, real_lemma",
    [
        ("nôhkom+N+A+D+Px1Sg+Sg", "nôhkom"),
        ("wâhkwa+N+A+Sg", "wâhkwa"),
        ("PV/yikate+tihtipinêw+V+TA+Ind+Prs+3Sg+4Sg/PlO", "tihtipinêw"),
        ("yîkatê-tihtipinam+V+TI+Ind+Prs+3Sg", "yîkatê-tihtipinam"),
        ("yîkatêpayin+V+II+Ind+Prs+3Sg", "yîkatêpayin"),
        ("tânisi+Ipc", "tânisi"),
        ("mitêh+N+I+D+PxX+Sg", "mitêh"),
        ("ôma+Pron+Def+Med+IN+Pl", "ôma"),
        ("ayinânêw+Num+Ipc", "ayinânêw"),
    ],
)
def test_hfstol_analysis_lemma_extraction(analysis, real_lemma):
    claimed = fst_analysis_parser.extract_lemma(analysis)
    assert claimed == real_lemma


@pytest.mark.parametrize(
    "analysis, category",
    [
        ("nôhkom+N+A+D+Px1Sg+Sg", LexicalCategory("NAD")),
        ("wâhkwa+N+A+Sg", LexicalCategory("NA")),
        ("PV/yikate+tihtipinêw+V+TA+Ind+Prs+3Sg+4Sg/PlO", LexicalCategory("VTA")),
        ("yîkatê-tihtipinam+V+TI+Ind+Prs+3Sg", LexicalCategory("VTI")),
        ("yîkatêpayin+V+II+Ind+Prs+3Sg", LexicalCategory("VII")),
        ("tânisi+Ipc", LexicalCategory("IPC")),
        ("mitêh+N+I+D+PxX+Sg", LexicalCategory("NID")),
        ("ôma+Pron+Def+Med+IN+Pl", LexicalCategory("PRON")),
    ],
)
def test_hfstol_analysis_category_extraction(analysis, category):
    actual = extract_category(analysis)
    assert actual == category


@pytest.mark.parametrize(
    "analyses,  lemma_analyses_index",
    [
        (["pîtatowêw+N+A+Sg"], [0]),
        (["okosisimâw+N+A+Sg", "okosisimêw+V+TA+Ind+Prs+X+3SgO"], [0]),
        (["nitêm+N+A+D+Px1Sg+Sg", "atim+N+A+Px1Sg+Sg"], [0]),
        (["pimiy+N+I+Der/Dim+N+I+Sg", "pimîs+N+I+Sg"], [1]),
        (["micisk+N+I+D+Px1Sg+Sg", "nicisk+N+I+D+Px1Sg+Sg"], []),
        (["ayâkonêw+V+II+Ind+Prs+3Sg", "ayâkonêw+V+AI+Ind+Prs+3Sg"], [0, 1]),
        (["âyiman+N+I+Sg", "âyiman+V+II+Ind+Prs+3Sg"], [0, 1]),
        (
            [
                "RdplW+pâstamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO+Err/Orth",
                "papâstamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO",
            ],
            [1],
        ),
        (
            [
                "RdplW+mâhcikwahpitam+V+TI+Ind+Prs+3Sg+Err/Orth",
                "mamâhcikwahpitam+V+TI+Ind+Prs+3Sg",
            ],
            [1],
        ),
        (["maskêk+N+I+Loc", "maskêkohk+Ipc"], [1]),
        (["ôma+Pron+Dem+Dist+I+Pl", "ôma+Pron+Def+Dist+I+Pl"], [0, 1]),
    ],
)
def test_identify(analyses, lemma_analyses_index):
    res = identify_lemma_analysis(analyses)
    assert len(lemma_analyses_index) == len(res)
    for i in lemma_analyses_index:
        assert analyses[i] in res


def test_l_text_extraction(shared_datadir):
    elements = (
        ET.parse(str(shared_datadir / "crkeng-missing-l-0.xml"))
        .getroot()
        .findall(".//e")
    )
    for element in elements:
        with pytest.raises(ValueError):
            extract_l_str(element)

    elements = (
        ET.parse(str(shared_datadir / "crkeng-nice-0.xml")).getroot().findall(".//e")
    )
    results = []
    for element in elements:
        results.append(extract_l_str(element))

    assert results == ["yôwamêw", "yôtinipahtâw"]
