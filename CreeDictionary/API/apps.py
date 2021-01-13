import logging
from pathlib import Path
from itertools import chain

from django.apps import AppConfig
from django.db import OperationalError
from utils import shared_res_dir
from utils.cree_lev_dist import remove_cree_diacritics

from .affix_search import AffixSearcher

logger = logging.getLogger(__name__)


def initialize_preverb_search():
    from django.db.models import Q

    from .models import Wordform

    # Hashing to speed up exhaustive preverb matching
    # so that we won't need to search from the database every time the user searches for a preverb or when the user
    # query contains a preverb
    # An all inclusive filtering mechanism is inflectional_category=IPV OR pos="IPV". Don't rely on a single one
    # due to the inconsistent labelling in the source crkeng.xml.
    # e.g. for preverb "pe", the source gives pos=Ipc ic=IPV.
    # For "sa", the source gives pos=IPV ic="" (unspecified)
    # after https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/pull/262
    # many preverbs are normalized so that both inflectional_category and pos are set to IPV.
    try:
        for preverb_wordform in Wordform.objects.filter(
            Q(inflectional_category="IPV") | Q(pos="IPV")
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


def initialize_affix_search() -> None:
    """
    Build tries and attach to Wordform class to facilitate prefix/suffix search
    """
    logger.info("Building tries for affix search...")
    from .models import (
        EnglishKeyword,
        Wordform,
        set_affix_searcher_for_english,
        set_combined_affix_searcher,
        set_affix_searcher_for_cree,
        affix_searcher_for_cree,
        affix_searcher_for_english,
    )

    try:
        Wordform.objects.count()
    except OperationalError:
        # apps.py will also get called during migration, it's possible that neither Wordform table nor text field
        # exists. Then an OperationalError will occur.
        logger.exception("Cannot build tries: Wordform table does not exist (yet)!")
        return

    set_affix_searcher_for_cree(AffixSearcher(fetch_cree_lemmas_with_ids()))
    set_affix_searcher_for_english(
        AffixSearcher((EnglishKeyword.objects.all().values_list("text", "lemma__id")))
    )

    set_combined_affix_searcher(
        _TemporaryComposeAffixSearchers(
            affix_searcher_for_cree(), affix_searcher_for_english()
        )
    )
    logger.info("Finished building tries")


def fetch_cree_lemmas_with_ids():
    """
    Return pairs of Cree lemmas with thier coorepsonding Wordform IDs.
    """
    from .models import Wordform

    return Wordform.objects.filter(is_lemma=True).values_list("text", "id")


class _TemporaryComposeAffixSearchers(AffixSearcher):
    def __init__(self, *searchers: AffixSearcher):
        self._searchers = searchers

    def search_by_prefix(self, prefix: str):
        return chain(
            *[searcher.search_by_prefix(prefix) for searcher in self._searchers]
        )

    def search_by_suffix(self, suffix: str):
        return chain(
            *[searcher.search_by_suffix(suffix) for searcher in self._searchers]
        )


class APIConfig(AppConfig):
    name = "API"

    def ready(self):
        """
        This function is called when you restart dev server or touch wsgi.py
        """
        initialize_preverb_search()
        initialize_affix_search()
        read_morpheme_rankings()
