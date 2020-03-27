import logging
from collections import defaultdict
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.db import connection, OperationalError
from typing import List, Dict, Set
import string

from .affix_search import AffixSearcher
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
    build tries and attach to Wordform class to facilitate prefix/suffix search
    """
    logger.info("Building tries for affix search...")
    from .models import Wordform

    cree_letter_to_ascii = {
        ascii_letter: ascii_letter for ascii_letter in string.ascii_lowercase
    }
    cree_letter_to_ascii.update(
        {"â": "a", "ā": "a", "ê": "e", "ē": "e", "ī": "i", "î": "i", "ô": "o", "ō": "o"}
    )
    try:
        lowered_no_diacritics_text_with_id = [
            ("".join([cree_letter_to_ascii.get(c, c) for c in text.lower()]), wf_id)
            for text, wf_id in Wordform.objects.filter(is_lemma=True).values_list(
                "text", "id"
            )
        ]
        # apps.py will also get called during migration, it's possible that neither Wordform table nor text field
        # exists. Then an OperationalError will occur.
    except OperationalError:
        return

    Wordform.affix_searcher = AffixSearcher(lowered_no_diacritics_text_with_id)
    logger.info("Finished building tries")


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
