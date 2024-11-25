from __future__ import annotations

import logging

from django.db.models import Q

from morphodict.utils import (
    get_modified_distance,
)
from morphodict.utils.english_keyword_extraction import stem_keywords
from morphodict.analysis import (
    strict_generator,
    rich_analyze_relaxed,
)
from morphodict.lexicon.models import Wordform, SourceLanguageKeyword
from morphodict.lexicon.util import to_source_language_keyword
from . import core
from .types import Result

logger = logging.getLogger(__name__)


def fetch_results(query: core.Query, search_results: core.SearchResults):
    # First collect some candidate results via keywords.
    # We split the query string into keywords, and collect all the entries that
    # match exactly as keywords in the database, both source and target.

    fetch_results_from_target_language_keywords(query, search_results)
    fetch_results_from_source_language_keywords(query, search_results)

    # Then we proceed to analyze the query, if successfull, we look for those 
    # entries in the dictionary that share the analysis with the FST result.
    # This introduces source-level spelling relaxation if the FST supports it.

    # Use the spelling relaxation to try to decipher the query
    #   e.g., "atchakosuk" becomes "acâhkos+N+A+Pl" --
    #         thus, we can match "acâhkos" in the dictionary!
    fst_analyses = set(rich_analyze_relaxed(query.query_string))
    # print([a.tuple for a in fst_analyses])

    db_matches = list(
        Wordform.objects.filter(raw_analysis__in=[a.tuple for a in fst_analyses])
    )

    for wf in db_matches:
        search_results.add_result(
            Result(
                wf,
                source_language_match=wf.text,
                query_wordform_edit_distance=get_modified_distance(
                    wf.text, query.query_string
                ),
            )
        )

        # An exact match here means we’re done with this analysis.
        fst_analyses.discard(wf.analysis)

    # fst_analyses has now been thinned by calls to `fst_analyses.remove()`
    # above; remaining items are analyses which are not in the database,
    # although their lemmas should be.
    #
    # Therefore, we will make on the go the extra entries.
    for analysis in fst_analyses:
        # When the user query is outside of paradigm tables
        # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
        # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+3Sg'}

        normatized_form_for_analysis = strict_generator().lookup(analysis.smushed())
        if len(normatized_form_for_analysis) == 0:
            logger.error(
                "Cannot generate normative form for analysis: %s (query: %s)",
                analysis,
                query.query_string,
            )
            continue

        # If there are multiple forms for this analysis, use the one that is
        # closest to what the user typed.
        normatized_user_query = min(
            normatized_form_for_analysis,
            key=lambda f: get_modified_distance(f, query.query_string),
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
            search_results.add_result(
                Result(
                    synthetic_wordform,
                    analyzable_inflection_match=True,
                    query_wordform_edit_distance=get_modified_distance(
                        query.query_string,
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

    lemmas_with_analyses = [wf for wf in possible_lemmas if wf.analysis]

    if len(lemmas_with_analyses) == 0:
        # Cannot figure out the intersection if we have no analyses!
        return possible_lemmas

    max_tag_intersection_count = max(
        analysis.tag_intersection_count(lwf.analysis) for lwf in lemmas_with_analyses
    )
    return [
        lwf
        for lwf in possible_lemmas
        if lwf.analysis
        and analysis.tag_intersection_count(lwf.analysis) == max_tag_intersection_count
    ]


def fetch_results_from_target_language_keywords(
    query: core.Query, search_results: core.SearchResults
):
    for stemmed_keyword in stem_keywords(query.query_string):
        for wordform in Wordform.objects.filter(
            target_language_keyword__text__iexact=stemmed_keyword
        ):
            search_results.add_result(
                Result(wordform, target_language_keyword_match=[stemmed_keyword])
            )


def fetch_results_from_source_language_keywords(
    query: core.Query, search_results: core.SearchResults
):
    res = SourceLanguageKeyword.objects.filter(
        Q(text=to_source_language_keyword(query.query_string))
    )
    for kw in res:
        search_results.add_result(
            Result(
                kw.wordform,
                source_language_keyword_match=[kw.text],
                query_wordform_edit_distance=get_modified_distance(
                    query.query_string, kw.wordform.text
                ),
            )
        )
