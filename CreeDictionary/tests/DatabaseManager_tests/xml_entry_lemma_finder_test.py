import pytest

from DatabaseManager.xml_entry_lemma_finder import extract_fst_lemmas


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [({"niya": [("Pron", "PrA")]}, {("niya", "Pron", "PrA"): "niya+Pron+Pers+1Sg"},)],
    [({"awa": [("Pron", "PrA")]}, {("niya", "Pron", "PrA"): "niya+Pron+Pers+1Sg"},)],
)
def test_lemma_extraction_pronoun(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [
        (
            {"yôwamêw": [("V", "VTA-1")]},
            {("yôwamêw", "V", "VTA-1"): "yôwamêw+V+TA+Ind+Prs+3Sg+4Sg/PlO"},
        )
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


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [({"ahin": [("V", "")]}, {("ahin", "V", ""): ""})],
)
def test_lemma_extraction_no_lemma_analysis_entry(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )


@pytest.mark.parametrize(
    ("xml_lemma_to_pos_lc", "expected_xml_lemma_pos_lc_to_fst_lemma"),
    [({"askiy": [("N", "NI-2")]}, {("askiy", "N", "NI-2"): ""})],
)
def test_lemma_extraction_ambiguous_lemma_analysis_entry(
    xml_lemma_to_pos_lc, expected_xml_lemma_pos_lc_to_fst_lemma
):
    assert (
        extract_fst_lemmas(xml_lemma_to_pos_lc, verbose=False)
        == expected_xml_lemma_pos_lc_to_fst_lemma
    )
