import logging
from collections import defaultdict
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.db import connection, OperationalError
from typing import List, Dict, Set
import string

from utils import shared_res_dir
from utils.cree_lev_dist import remove_cree_diacritics

logger = logging.getLogger(__name__)


def initialize_fuzzy_search():
    # todo: fuzzy search is for now not used. Use it in the future
    # # without the guard
    # # on travis this line of code will be run before a database exist and will error
    # if "API_inflection" in connection.introspection.table_names():
    #     # Have to do it locally, or will get error (apps aren't loaded yet)
    #     from API.models import Inflection
    #
    #     Inflection.init_fuzzy_searcher()
    pass


def initialize_preverb_search():
    from .models import Wordform
    from django.db.models import Q

    # Hashing to speed up exhaustive preverb matching
    # so that we won't need to search from the database every time the user searches for a preverb or when the user
    # query contains a preverb

    # An all inclusive filtering mechanism is full_lc=IPV OR pos="IPV". Don't rely on a single one
    # due to the inconsistent labelling in the source crkeng.xml.
    # e.g. for preverb "pe", the source gives pos=Ipc lc=IPV.
    # For "sa", the source gives pos=IPV lc="" (unspecified)

    # after https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/pull/262
    # many preverbs are normalized so that both full_lc and pos are set to IPV.
    try:
        for preverb_wordform in Wordform.objects.filter(
            Q(full_lc="IPV") | Q(pos="IPV")
        ):
            if not preverb_wordform.md_only:
                Wordform.PREVERB_ASCII_LOOKUP[
                    remove_cree_diacritics(preverb_wordform.text.strip("-"))
                ].add(preverb_wordform)
    except OperationalError:
        # the ready function gets called during `$ manage-db import` when one builds the database from scratch
        # At that time, while the migrations are not applied, Wordform tables does not exist.
        pass


def read_morpheme_rankings():
    from .models import Wordform

    lines = (
        Path(shared_res_dir / "W_aggr_corp_morph_log_freq.txt").read_text().splitlines()
    )
    for line in lines:
        cells = line.split("\t")
        # todo: use the third row
        if len(cells) >= 2:
            freq, morpheme, *_ = cells
            Wordform.MORPHEME_RANKINGS[morpheme] = float(freq)


def initialize_affix_search():
    """
    build dictionaries as Wordform class attributes to facilitate affix search
    """
    from .models import Wordform

    try:
        lemma_wordforms = Wordform.objects.filter(is_lemma=True)
    except OperationalError:
        # when past version of the database is yet to migrate all the changes,
        # we might not have Wordform table, is_lemma field in the database
        return

    logger.info("Building affix search dictionaries")
    # how many letters from the start/end do we check, larger length means more memory used, longer initialization time, but faster search
    length = settings.AFFIX_SEARCH_LENGTH

    n_th_letter_to_lemma_wordform_ids: List[Dict[str, Set[int]]] = [
        defaultdict(set) for _ in range(length)
    ]
    inverse_n_th_letter_to_lemma_wordform_ids: List[Dict[str, Set[int]]] = [
        defaultdict(set) for _ in range(length)
    ]

    cree_letter_to_ascii = {
        ascii_letter: ascii_letter for ascii_letter in string.ascii_lowercase
    }
    cree_letter_to_ascii.update(
        {"â": "a", "ā": "a", "ê": "e", "ē": "e", "ī": "i", "î": "i", "ô": "o", "ō": "o"}
    )

    for wf in lemma_wordforms:
        lowered_wf_text = wf.text.lower()

        for i in range(length):
            try:
                lowered_letter = lowered_wf_text[i]
            except IndexError:
                break
            n_th_letter_to_lemma_wordform_ids[i][
                cree_letter_to_ascii.get(lowered_letter, lowered_letter)
            ].add(wf.id)

        for i in range(length):
            try:
                lowered_letter = lowered_wf_text[-i - 1]
            except IndexError:
                break

            inverse_n_th_letter_to_lemma_wordform_ids[i][
                cree_letter_to_ascii.get(lowered_letter, lowered_letter)
            ].add(wf.id)

    Wordform.N_TH_LETTER_TO_LEMMA_IDS = n_th_letter_to_lemma_wordform_ids
    Wordform.INVERSE_N_TH_LETTER_TO_LEMMA_IDS = (
        inverse_n_th_letter_to_lemma_wordform_ids
    )
    logger.info("Finished building affix search dictionaries...")


class APIConfig(AppConfig):
    name = "API"

    def ready(self):
        """
        This function is called prior to app start.
        It initializes fuzzy search (build the data structure).
        It also hashes preverbs for faster preverb matching.
        """
        initialize_fuzzy_search()
        initialize_preverb_search()
        initialize_affix_search()
        read_morpheme_rankings()
