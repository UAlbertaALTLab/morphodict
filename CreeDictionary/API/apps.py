import logging
import os
from pathlib import Path

from django.apps import AppConfig, apps
from django.db import OperationalError
from django.db.models import Q

from utils import shared_res_dir
from utils.cree_lev_dist import remove_cree_diacritics

logger = logging.getLogger(__name__)


class APIConfig(AppConfig):
    name = "API"

    def ready(self) -> None:
        # This function is called when you restart dev server or touch wsgi.py
        #
        # Avoid using this method. It gets called during startup of *every*
        # management command, wasting time, and when you’re running tests, the
        # database config inside this method can point at the production
        # database (!!)
        #
        # https://docs.djangoproject.com/en/3.1/ref/applications/#django.apps.AppConfig.ready
        #
        # For when you you really want eager loading:
        #   - The runserver auto-reloading sets a RUN_MAIN environment variable
        #   - Our wsgi.py sets PERFORM_TIME_CONSUMING_INITIALIZATIONS
        if (
            "RUN_MAIN" in os.environ
            or "PERFORM_TIME_CONSUMING_INITIALIZATIONS" in os.environ
        ):
            self.perform_time_consuming_initializations()

    def perform_time_consuming_initializations(self):
        from API.search import affix

        logger.debug("loading affix caches")
        affix.cache.preload()

        logger.debug("calling initialize_preverb_search()")
        initialize_preverb_search()

        logger.debug("calling read_morpheme_rankings()")
        read_morpheme_rankings()

        logger.debug("done")

    @classmethod
    def active_instance(cls) -> "APIConfig":
        """
        Fetch the instance of this Config from the Django app registry.

        This way you can get access to the affix searchers in other modules!
        """
        return apps.get_app_config(cls.name)


def initialize_preverb_search():
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

    def has_non_md_non_auto_definitions(wordform):
        "This may look slow, but isn’t if prefetch_related has been used"
        for d in wordform.definitions.all():
            for c in d.citations.all():
                if c.abbrv not in ["auto", "MD"]:
                    return True
        return False

    try:
        queryset = Wordform.objects.filter(
            Q(inflectional_category="IPV") | Q(pos="IPV")
        ).prefetch_related("definitions__citations")
        for preverb_wordform in queryset:
            if has_non_md_non_auto_definitions(preverb_wordform):
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
