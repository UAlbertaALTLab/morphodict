from pathlib import Path

from CreeDictionary.utils import shared_res_dir

DOCUMENT_FREQUENCY = {}
NORMALIZED_FREQUENCIES = {}


def get_glossary_count(search_run):
    prep_freqs()
    [find_glossary_count(result) for result in search_run.unsorted_results()]


def prep_freqs():
    lines = (
        Path(shared_res_dir / "crk_glossaries_aggregate_vocab.txt")
            .read_text()
            .splitlines()
    )
    max = -1
    for line in lines:
        cells = line.split("\t")
        # todo: use the third row
        if len(cells) >= 2:
            freq, morpheme, *_ = cells
            if int(freq) > max:
                max = int(freq)
            DOCUMENT_FREQUENCY[morpheme] = int(freq)

    for morph in DOCUMENT_FREQUENCY:
        NORMALIZED_FREQUENCIES[morph] = DOCUMENT_FREQUENCY[morph] / max


def find_glossary_count(result):
    if result.lemma_wordform.text in DOCUMENT_FREQUENCY:
        result.glossary_count = DOCUMENT_FREQUENCY[result.lemma_wordform.text]
        return
    result.glossary_count = 0
    return
