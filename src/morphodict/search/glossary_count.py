from pathlib import Path

from morphodict.utils import shared_res_dir

DOCUMENT_FREQUENCY = {}


def get_glossary_count(search_run):
    prep_freqs()
    [find_glossary_count(result) for result in search_run.unsorted_results()]


def prep_freqs():
    # print(
    #     "Location of glossary file:",
    #     Path(shared_res_dir / "crk_glossaries_aggregate_vocab.txt"),
    # )
    lines = (
        Path(shared_res_dir / "crk_glossaries_aggregate_vocab.txt")
        .read_text()
        .splitlines()
    )
    max = 3
    for line in lines:
        cells = line.split("\t")
        if len(cells) >= 2:
            freq, morpheme, *_ = cells
            # normalize by dividing by max
            DOCUMENT_FREQUENCY[morpheme] = int(freq) / max


def find_glossary_count(result):
    if result.lemma_wordform.text in DOCUMENT_FREQUENCY:
        result.glossary_count = DOCUMENT_FREQUENCY[result.lemma_wordform.text]
        return
    result.glossary_count = 0
    return
