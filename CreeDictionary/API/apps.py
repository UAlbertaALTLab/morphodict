from django.apps import AppConfig
from django.db import connection, OperationalError

from utils.cree_lev_dist import remove_cree_diacritics


class APIConfig(AppConfig):
    name = "API"

    def ready(self):
        """
        This function is called prior to app start.
        It initializes fuzzy search (build the data structure).
        It also hashes preverbs for faster preverb matching.
        """
        # todo: fuzzy search is for now not used. Use it in the future
        # # without the guard
        # # on travis this line of code will be run before a database exist and will error
        # if "API_inflection" in connection.introspection.table_names():
        #     # Have to do it locally, or will get error (apps aren't loaded yet)
        #     from API.models import Inflection
        #
        #     Inflection.init_fuzzy_searcher()

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
