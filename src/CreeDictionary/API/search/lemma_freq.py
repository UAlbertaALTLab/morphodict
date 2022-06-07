from pathlib import Path

from CreeDictionary.utils import shared_res_dir

LEMMA_FREQUENCY = {}
NORMALIZED_FREQUENCIES = {}


def load_lemma_data():
    lines = Path(shared_res_dir / "lemma_frequency.txt").read_text().splitlines()
    max = -1
    for line in lines:
        cells = line.split("\t")
        # todo: use the third row
        if len(cells) >= 2:
            a_freq, a, l_freq, l, b, c, d, e = cells
            if l not in LEMMA_FREQUENCY:
                if int(l_freq) > max:
                    max = int(l_freq)
                LEMMA_FREQUENCY[l] = int(l_freq)

    for lemma in LEMMA_FREQUENCY:
        NORMALIZED_FREQUENCIES[lemma] = LEMMA_FREQUENCY[lemma] / max


def get_lemma_freq(search_run):
    load_lemma_data()
    [find_lemma_freq(result) for result in search_run.unsorted_results()]


def find_lemma_freq(result):
    if result.lemma_wordform.text in NORMALIZED_FREQUENCIES:
        result.lemma_freq = NORMALIZED_FREQUENCIES[result.lemma_wordform.text]
        return
    result.lemma_freq = 0
