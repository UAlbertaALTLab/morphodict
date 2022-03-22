from pathlib import Path

from CreeDictionary.utils import shared_res_dir

DOCUMENT_FREQUENCY = {}


def get_document_frequency(search_run):
    prep_freqs()
    for result in search_run.unsorted_results():
        result.document_freq = find_document_freq(result)


def prep_freqs():
    lines = (
        Path(shared_res_dir / "crk_glossaries_aggregate_vocab.txt")
            .read_text()
            .splitlines()
    )
    for line in lines:
        cells = line.split("\t")
        # todo: use the third row
        if len(cells) >= 2:
            freq, morpheme, *_ = cells
            DOCUMENT_FREQUENCY[morpheme] = int(freq)


def find_document_freq(result):
    if result.lemma_wordform.text in DOCUMENT_FREQUENCY:
        return DOCUMENT_FREQUENCY[result.lemma_wordform.text]
    return 0
