from io import StringIO
from textwrap import dedent
from typing import List, Tuple

import pytest
from CreeDictionary.DatabaseManager.xml_entry_lemma_finder import identify_entries
from CreeDictionary.utils.crkeng_xml_utils import IndexedXML
from CreeDictionary.utils.data_classes import XMLEntry, XMLTranslation


def _xml_translation_to_str(xml_translation: XMLTranslation) -> str:
    #   pos??
    #   pos of a translation is not imported anywhere nor used anywhere
    #   It's safe to leave it blank here
    return dedent(
        f"""
            <t pos="" sources="{' '.join(xml_translation.sources)}">{xml_translation.text}</t>
        """
    ).strip()


def _xml_entry_to_str(xml_entry: XMLEntry) -> str:
    mg_template = """
                    <mg>
                        <tg xml:lang="eng">
                            {}
                        </tg>
                    </mg>"""
    mgs = "\n".join(
        [mg_template.format(_xml_translation_to_str(t)) for t in xml_entry.translations]
    )

    if xml_entry.stem is None:
        stem_element_string = ""
    else:
        stem_element_string = "<stem>" + xml_entry.stem + "</stem>"

    return dedent(
        f"""
            <e>
                <lg>
                    <l pos="{xml_entry.pos}">{xml_entry.l}</l>
                    <lc>{xml_entry.ic}</lc>
                    {stem_element_string}
                </lg>
                {mgs}
            </e>
        """
    ).strip()


def _create_in_memory_crkeng(entries: List[XMLEntry]) -> StringIO:
    template = dedent(
        """
    <r>
        <source id="CW">
            <title>Cree : Words / nēhiyawēwin : itwēwina</title>
        </source>
        <source id="MD">
            <title>Maskwacîs Cree Dictionary</title>
        </source>
        {}
    </r>
    """
    ).strip()

    return StringIO(template.format("\n".join([_xml_entry_to_str(e) for e in entries])))


@pytest.mark.parametrize(
    ("entry_lemma_pos_ic", "expected_analysis"),
    [
        (
            ("yôwamêw", "V", "VTA-1"),
            "yôwamêw+V+TA+Ind+3Sg+4Sg/PlO",
        ),
        (("ahin", "V", ""), "ahêw+V+TA+Ind+3Sg+4Sg/PlO"),
    ],
)
def test_lemma_extraction_single_identifiable_entry(
    entry_lemma_pos_ic: Tuple[str, str, str], expected_analysis
):
    lemma, pos, ic = entry_lemma_pos_ic
    entry = XMLEntry(l=lemma, pos=pos, ic=ic, stem=None, translations=())
    indexed_xml = IndexedXML.from_xml_file(_create_in_memory_crkeng([entry]))

    assert identify_entries(indexed_xml, verbose=False) == (
        {entry: expected_analysis},
        [],
    )


@pytest.mark.parametrize(
    ("entry_lemma_pos_ic",),
    [(("yêkawiskâwikamâhk", "N", "INM"),)],
)
def test_lemma_extraction_unidentifiable_entry(
    entry_lemma_pos_ic: Tuple[str, str, str]
):
    lemma, pos, ic = entry_lemma_pos_ic
    entry = XMLEntry(l=lemma, pos=pos, ic=ic, stem=None, translations=())
    indexed_xml = IndexedXML.from_xml_file(_create_in_memory_crkeng([entry]))

    assert identify_entries(indexed_xml, verbose=False) == ({}, [entry])


# @pytest.mark.parametrize(
#     ("xml_lemma_to_pos_ic", "expected_xml_lemma_pos_ic_to_fst_lemma"), [()],
# )
# def test_lemma_extraction_no_lemma_analysis_entry(
#     xml_lemma_to_pos_ic, expected_xml_lemma_pos_ic_to_fst_lemma
# ):
#     # todo: have an example of some word that only exists in MD and can not even by analysed by strict analyzer
#     assert (
#         extract_fst_lemmas(xml_lemma_to_pos_ic, verbose=False)
#         == expected_xml_lemma_pos_ic_to_fst_lemma
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


def test_lemma_extraction_ambiguous_lemma_analysis_entry():

    askiy_entry = XMLEntry(l="askiy", pos="N", ic="NI-2", stem=None, translations=())
    ayiwinis_entry = XMLEntry(
        l="ayiwinis", pos="", ic="NI-2", stem=None, translations=()
    )

    indexed_xml = IndexedXML.from_xml_file(
        _create_in_memory_crkeng([askiy_entry, ayiwinis_entry])
    )

    assert identify_entries(indexed_xml, verbose=False) == (
        {askiy_entry: "askiy+N+I+Sg"},
        [ayiwinis_entry],
    )
