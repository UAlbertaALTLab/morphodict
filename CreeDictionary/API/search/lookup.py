from __future__ import annotations

import logging
from typing import Iterable, Set

from django.db.models import Q

from API.models import (
    Wordform,
    EnglishKeyword,
    wordform_cache,
)
from CreeDictionary import hfstol
from utils import get_modified_distance, fst_analysis_parser, PartOfSpeech
from utils.cree_lev_dist import remove_cree_diacritics
from utils.english_keyword_extraction import stem_keywords
from utils.types import ConcatAnalysis
from .types import Result
from . import core

logger = logging.getLogger(__name__)


def fetch_results(search_run: core.SearchRun):
    """
    The rest of this method is code Eddie has NOT refactored, so I don't really
    understand what's going on here:
    """
    # Use the spelling relaxation to try to decipher the query
    #   e.g., "atchakosuk" becomes "acâhkos+N+A+Pl" --
    #         thus, we can match "acâhkos" in the dictionary!
    fst_analyses: Set[ConcatAnalysis] = set(
        a.concatenate() for a in hfstol.analyze(search_run.internal_query)
    )

    all_standard_forms = []

    for analysis in fst_analyses:
        # todo: test

        exactly_matched_wordforms = Wordform.objects.filter(
            analysis=analysis, as_is=False
        )

        if exactly_matched_wordforms.exists():
            for wf in exactly_matched_wordforms:
                search_run.add_result(
                    Result(
                        wf,
                        source_language_match=wf.text,
                        query_wordform_edit_distance=get_modified_distance(
                            wf.text, search_run.internal_query
                        ),
                    )
                )
        else:
            # When the user query is outside of paradigm tables
            # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
            # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+3Sg'}

            lemma_wc = fst_analysis_parser.extract_lemma_text_and_word_class(analysis)
            if lemma_wc is None:
                logger.error(
                    f"fst_analysis_parser cannot understand analysis {analysis}"
                )
                continue

            # now we generate the standardized form of the user query for display purpose
            normatized_form_for_analysis = list(hfstol.generate(analysis))
            all_standard_forms.extend(normatized_form_for_analysis)
            if len(normatized_form_for_analysis) == 0:
                logger.error(
                    "Cannot generate normative form for analysis: %s (query: %s)",
                    analysis,
                    search_run.internal_query,
                )
                continue

            normatized_user_query = min(
                normatized_form_for_analysis,
                key=lambda f: get_modified_distance(f, search_run.internal_query),
            )

            lemma, word_class = lemma_wc
            matched_lemma_wordforms = Wordform.objects.filter(text=lemma, is_lemma=True)

            # now we get wordform objects from database
            # Note:
            # non-analyzable matches should not be displayed (mostly from MD)
            # like "nipa", which means kill him
            # those results are filtered out by `as_is=False` below
            # suggested by Arok Wolvengrey

            if word_class.pos is PartOfSpeech.PRON:
                # specially handle pronouns.
                # this is a temporary fix, otherwise "ôma" won't appear in the search results, since
                # "ôma" has multiple analysis
                # ôma+Ipc+Foc
                # ôma+Pron+Dem+Prox+I+Sg
                # ôma+Pron+Def+Prox+I+Sg
                # it's ambiguous which one is the lemma in the importing process thus it's labeled "as_is"

                # a more permanent fix requires every pronouns lemma to be listed and specified
                for lemma_wordform in matched_lemma_wordforms:
                    synthetic_wordform = Wordform(
                        text=normatized_user_query,
                        pos=PartOfSpeech.PRON,
                        analysis=analysis,
                        lemma=lemma_wordform,
                    )
                    search_run.add_result(
                        Result(
                            synthetic_wordform,
                            pronoun_as_is_match=True,
                            query_wordform_edit_distance=get_modified_distance(
                                search_run.internal_query,
                                normatized_user_query,
                            ),
                        )
                    )
            else:
                for lemma_wordform in matched_lemma_wordforms.filter(
                    as_is=False, pos=word_class.pos.name
                ):
                    synthetic_wordform = Wordform(
                        lemma=lemma_wordform,
                        analysis=analysis,
                        pos=word_class.pos.name,
                        text=normatized_user_query,
                    )
                    search_run.add_result(
                        Result(
                            synthetic_wordform,
                            analyzable_inflection_match=True,
                            query_wordform_edit_distance=get_modified_distance(
                                search_run.internal_query, normatized_user_query
                            ),
                        )
                    )

    # we choose to trust CW and show those matches with definition from CW.
    # text__in = all_standard_forms help match those lemmas that are labeled as_is but trust-worthy nonetheless
    # because they come from CW
    # text__in = [user_query] help matching entries with spaces in it, which fst can't analyze.
    for cw_as_is_wordform in filter_cw_wordforms(
        Wordform.objects.filter(
            text__in=all_standard_forms + [search_run.internal_query],
            as_is=True,
            is_lemma=True,
        )
    ):
        search_run.add_result(
            Result(
                cw_as_is_wordform,
                is_cw_as_is_wordform=True,
                query_wordform_edit_distance=get_modified_distance(
                    search_run.internal_query, cw_as_is_wordform.text
                ),
            )
        )

    # as per https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
    # preverbs should be presented
    # exhaustively search preverbs here (since we can't use fst on preverbs.)
    for preverb_wf in fetch_preverbs(search_run.internal_query):
        search_run.add_result(
            Result(
                preverb_wf,
                is_preverb_match=True,
                query_wordform_edit_distance=get_modified_distance(
                    preverb_wf.text, search_run.internal_query
                ),
            )
        )

    # now we get results searched by English
    for stemmed_keyword in stem_keywords(search_run.internal_query):
        for wordform in Wordform.objects.filter(
            english_keyword__text__iexact=stemmed_keyword
        ):
            search_run.add_result(
                Result(wordform, target_language_keyword_match=[stemmed_keyword])
            )


def filter_cw_wordforms(queryset: Iterable[Wordform]) -> Iterable[Wordform]:
    """
    return the wordforms that has definition from CW dictionary

    :param queryset: an Iterable of Wordforms
    """
    for wordform in queryset:
        for definition in wordform.definitions.all():
            if "CW" in definition.source_ids:
                yield wordform
                break


def fetch_preverbs(user_query: str) -> Set[Wordform]:
    """
    Search for preverbs in the database by matching the circumflex-stripped forms. MD only contents are filtered out.
    trailing dash relaxation is used

    :param user_query: unicode normalized, to_lower-ed
    """

    if user_query.endswith("-"):
        user_query = user_query[:-1]
    user_query = remove_cree_diacritics(user_query)

    return wordform_cache.PREVERB_ASCII_LOOKUP[user_query]
