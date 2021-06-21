from __future__ import annotations

import logging

from django.db.models import Q

from CreeDictionary.utils import (
    get_modified_distance,
)
from CreeDictionary.utils.english_keyword_extraction import stem_keywords
from morphodict.analysis import (
    strict_generator,
    rich_analyze_relaxed,
)
from morphodict.lexicon.models import Wordform, SourceLanguageKeyword
from morphodict.lexicon.util import strip_accents_for_search_lookups
from . import core
from .types import Result

logger = logging.getLogger(__name__)


def fetch_results(search_run: core.SearchRun):
    fetch_results_from_target_language_keywords(search_run)
    fetch_results_from_source_language_keywords(search_run)

    # Use the spelling relaxation to try to decipher the query
    #   e.g., "atchakosuk" becomes "acâhkos+N+A+Pl" --
    #         thus, we can match "acâhkos" in the dictionary!
    fst_analyses = rich_analyze_relaxed(search_run.internal_query)

    db_matches = list(
        Wordform.objects.filter(raw_analysis__in=[a.tuple for a in fst_analyses])
    )

    for wf in db_matches:
        search_run.add_result(
            Result(
                wf,
                source_language_match=wf.text,
                query_wordform_edit_distance=get_modified_distance(
                    wf.text, search_run.internal_query
                ),
            )
        )

        # An exact match here means we’re done with this analysis.
        assert wf.analysis in fst_analyses, "wordform analysis not in search set"
        fst_analyses.remove(wf.analysis)

    # fst_analyses has now been thinned by calls to `fst_analyses.remove()`
    # above; remaining items are analyses which are not in the database,
    # although their lemmas should be.
    for analysis in fst_analyses:
        # When the user query is outside of paradigm tables
        # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
        # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+3Sg'}

        normatized_form_for_analysis = strict_generator().lookup(analysis.smushed())
        if len(normatized_form_for_analysis) == 0:
            logger.error(
                "Cannot generate normative form for analysis: %s (query: %s)",
                analysis,
                search_run.internal_query,
            )
            continue

        # If there are multiple forms for this analysis, use the one that is
        # closest to what the user typed.
        normatized_user_query = min(
            normatized_form_for_analysis,
            key=lambda f: get_modified_distance(f, search_run.internal_query),
        )

        possible_lemma_wordforms = best_lemma_matches(
            analysis, Wordform.objects.filter(text=analysis.lemma, is_lemma=True)
        )

        for lemma_wordform in possible_lemma_wordforms:
            synthetic_wordform = Wordform(
                text=normatized_user_query,
                raw_analysis=analysis.tuple,
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


def best_lemma_matches(analysis, possible_lemmas) -> list[Wordform]:
    """
    Return best matches between analysis and potentially matching lemmas

    The following example is in Plains Cree but the algorithm should be good
    enough for any language.

    nikîmôci-nêwokâtânân has analysis PV/kimoci+nêwokâtêw+V+AI+Ind+1Pl

    Which of the three lemmas for nêwokâtêw should that be matched to?

    Let’s take the ones with the most tags in common.

                                    Tags in common    Winner
        nêwokâtêw+N+A+Sg            0
        nêwokâtêw+V+AI+Ind+3Sg      3   +V +AI +Ind   *
        nêwokâtêw+V+II+Ind+3Sg      2   +V +Ind

    We may get better results if we have, for the wordform language, a list of
    lexical tags like +V to consider as opposed to inflectional tags like +3Sg.
    """
    possible_lemmas = possible_lemmas[:]
    if len(possible_lemmas) < 2:
        return possible_lemmas

    max_tag_intersection_count = max(
        analysis.tag_intersection_count(lwf.analysis) for lwf in possible_lemmas
    )
    return [
        lwf
        for lwf in possible_lemmas
        if analysis.tag_intersection_count(lwf.analysis) == max_tag_intersection_count
    ]


def fetch_results_from_target_language_keywords(search_run):
    for stemmed_keyword in stem_keywords(search_run.internal_query):
        for wordform in Wordform.objects.filter(
            target_language_keyword__text__iexact=stemmed_keyword
        ):
            search_run.add_result(
                Result(wordform, target_language_keyword_match=[stemmed_keyword])
            )


def fetch_results_from_source_language_keywords(search_run):
    res = SourceLanguageKeyword.objects.filter(
        Q(text=search_run.internal_query)
        | Q(text=strip_accents_for_search_lookups(search_run.internal_query).lower())
    )
    for kw in res:
        search_run.add_result(
            Result(
                kw.wordform,
                source_language_keyword_match=[kw.text],
                query_wordform_edit_distance=get_modified_distance(
                    search_run.internal_query, kw.wordform.text
                ),
            )
        )
