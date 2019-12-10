import pytest

from DatabaseManager.xml_entry_lemma_finder import extract_fst_lemmas


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [
        (
            {"yôwamêw": [("V", "VTA-1")]},
            {("yôwamêw", "V", "VTA-1"): "yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"},
        ),
        ({"ahin": [("V", "")]}, {("ahin", "V", ""): "ahêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"}),
    ],
)
def test_lemma_extraction_behaving_entry(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [({"yêkawiskâwikamâhk": [("N", "INM")]}, {("yêkawiskâwikamâhk", "N", "INM"): ""})],
)
def test_lemma_extraction_no_analysis_entry(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )


# @pytest.mark.parametrize(
#     ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"), [()],
# )
# def test_lemma_extraction_no_lemma_analysis_entry(
#     xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
# ):
#     # todo: have an example of some word that only exists in MD and  can not even by analysed by strict analyzer
#     assert (
#         extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
#         == expected_xml_lemma_pos_lc_to_fst_lemma
#     )


# regarding the cause of ambiguity and its consequences. See:
# https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/176
# explanation of the resolution process of these two test cases:


# askiy (label in xml file: N NI-2)
# askiy   askiya+N+I+Sg
# askiy   askiy+N+I+Sg

# ayiwinis (label in xml file: N NI-2)
# ayiwinis        ayiwinisa+N+I+Sg
# ayiwinis        ayiwin+N+I+Der/Dim+N+I+Sg

# askiy has two potential NI analyses. The second wordform look the same, choose the second

# ayiwinis has two potential NI analysis, non look the same, label it as ambiguous


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [
        (
            {"askiy": [("N", "NI-2")], "ayiwinis": [("", "NI-1")]},
            {("askiy", "N", "NI-2"): "askiy+N+I+Sg", ("ayiwinis", "", "NI-1"): ""},
        )
    ],
)
def test_lemma_extraction_ambiguous_lemma_analysis_entry(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )
