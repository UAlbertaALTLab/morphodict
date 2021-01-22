import logging
from functools import cached_property
from pathlib import Path

from django.apps import AppConfig, apps
from django.db import OperationalError

from utils import shared_res_dir
from utils.cree_lev_dist import remove_cree_diacritics
from .affix_search import AffixSearcher

logger = logging.getLogger(__name__)


class APIConfig(AppConfig):
    name = "API"

    @cached_property
    def cree_affix_searcher(self) -> AffixSearcher:
        return AffixSearcher(fetch_cree_lemmas_with_ids())

    @cached_property
    def english_affix_searcher(self) -> AffixSearcher:
        return AffixSearcher(fetch_english_keywords_with_ids())

    def ready(self) -> None:
        # FIXME don’t use this method, it gets called during startup of *every*
        # management command, wasting time, and when you’re running tests, the
        # database config inside this method can point at the production
        # database (!!)
        #
        # https://docs.djangoproject.com/en/3.1/ref/applications/#django.apps.AppConfig.ready
        #
        # Suggestions if you really want eager loading:
        #   - The runserver auto-reloading sets a RUN_MAIN environment variable, you
        #     could set that
        #   - wsgi.py could set something too
        """
        This function is called when you restart dev server or touch wsgi.py
        """
        initialize_preverb_search()
        read_morpheme_rankings()

    @classmethod
    def active_instance(cls) -> "APIConfig":
        """
        Fetch the instance of this Config from the Django app registry.

        This way you can get access to the affix searchers in other modules!
        """
        return apps.get_app_config(cls.name)


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


def fetch_english_keywords_with_ids():
    """
    Return pairs of indexed English keywords with their coorepsonding Wordform IDs.
    """
    from .models import EnglishKeyword

    return EnglishKeyword.objects.all().values_list("text", "lemma__id")


def fetch_cree_lemmas_with_ids():
    """
    Return pairs of Cree lemmas with their coorepsonding Wordform IDs.
    """
    from .models import Wordform

    return Wordform.objects.filter(is_lemma=True).values_list("text", "id")
