from pathlib import Path

from morphodict.utils import shared_res_dir

LEMMA_FREQUENCY = {}


def load_lemma_data():
    lines = Path(shared_res_dir / "lemma_frequency.txt").read_text().splitlines()
    # max = 32334
    for line in lines:
        cells = line.split("\t")
        if len(cells) >= 2:
            a_freq, a, l_freq, l, b, c, d, e = cells
            if l not in LEMMA_FREQUENCY:
                # we want to normalize the lemma frequency
                # so I found the max of 32334
                # and now we divide by that
                LEMMA_FREQUENCY[l] = int(l_freq) #/ max


def get_lemma_freq(search_results):
    load_lemma_data()
    [find_lemma_freq(result) for result in search_results.unsorted_results()]


def find_lemma_freq(result):
    if result.lemma_wordform.text in LEMMA_FREQUENCY:
        result.lemma_freq = LEMMA_FREQUENCY[result.lemma_wordform.text]
        return
    result.lemma_freq = 0
