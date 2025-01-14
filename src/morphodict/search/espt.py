"""
ESPT: English simple phrase translation
"""

import logging
from dataclasses import dataclass

from morphodict.phrase_translate.tag_maps import (
    verb_tag_map,
    noun_tag_map,
    source_noun_tags,
)

from morphodict.search.types import Result
from morphodict.search.core import SearchResults
from morphodict.search.query import Query
from morphodict.phrase_translate.types import PhraseAnalyzedQuery
from morphodict.analysis import RichAnalysis
from morphodict.analysis.tag_map import UnknownTagError
from morphodict.lexicon.models import Wordform
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class _EipResult:
    """Tiny class to connect inflected text to original search result"""

    inflected_text: str
    analysis: RichAnalysis
    original_result: Result


class EsptSearch:
    """An English simple phrase translation search.

    There are two phases:
     1. analyzing the original query to determine if it is a phrase search.
     2. using tags extracted from phase #1 to inflect search results obtained by
        other methods.
    """

    def __init__(self, query: Query, search_results: SearchResults):
        self.search_results = search_results
        self.query = query
        self.query_analyzed_ok = False
        self.tags = None

    def convert_search_query_to_espt(self):
        """Analyze this search’s search_results query, possibly updating it.

        If the phrase-parsing FST returns an analysis, e.g., “ crawls
        +V+AI+Prt+3Pl” for “they crawled”, then the tags are saved for
        inflecting search results later, and the query is updated to only
        include content words, e.g., “they crawled” → “crawls”.
        """
        self.new_tags = []
        analyzed_query = PhraseAnalyzedQuery(
            self.query.query_string,
            add_verbose_message=self.search_results.add_verbose_message,
        )
        if analyzed_query.has_tags:
            if "+N" in analyzed_query.tags:
                tag_map = noun_tag_map
            elif "+V" in analyzed_query.tags:
                tag_map = verb_tag_map
            else:
                return

            try:
                self.new_tags = tag_map.map_tags(analyzed_query.tags)
            except UnknownTagError as e:
                logger.error(f"Unable to map tags for {analyzed_query}", exc_info=True)
                self.search_results.add_verbose_message(espt_analysis_error=repr(e))
                return

            self.query.replace_query(analyzed_query.filtered_query)
            self.query_analyzed_ok = True

        self.search_results.add_verbose_message(
            filtered_query=analyzed_query.filtered_query,
            tags=analyzed_query.tags,
            new_tags=self.new_tags,
        )
        self.tags = analyzed_query.tags

    def inflect_search_results(self):
        if not self.query_analyzed_ok:
            return

        inflected_results = self._generate_inflected_results()

        # aggregating queries for performance
        possible_wordforms = Wordform.objects.filter(
            text__in=[r.inflected_text for r in inflected_results]
        )
        wordform_lookup = {}
        for wf in possible_wordforms:
            wordform_lookup[(wf.text, wf.lemma_id)] = wf

        for result in inflected_results:
            wordform = wordform_lookup.get(
                (result.inflected_text, result.original_result.lemma_wordform.id)
            )
            if wordform is None:
                # inflected form not found in DB, so create a synthetic one. Can
                # happen for Plains Cree, when the EIP search produces a valid
                # analysis not covered by any paradigm file.
                #
                # Note: would not have auto-translations since those are
                # currently only available for wordforms that were previously
                # saved in the DB.
                lemma = result.original_result.lemma_wordform

                wordform = Wordform(
                    text=result.inflected_text,
                    lemma=lemma,
                    raw_analysis=result.analysis.tuple,
                )

            # if there are multiple inflections for the same original result, we
            # may already have removed it
            if self.search_results.has_result(result.original_result):
                self.search_results.remove_result(result.original_result)

            self.search_results.add_result(
                result.original_result.create_related_result(
                    wordform,
                    is_espt_result=True,
                )
            )

    def _collect_non_inflected_results(self) -> list[Result]:
        words = []
        for r in self.search_results.unsorted_results():
            if not r.is_lemma:
                continue
            analysis = r.wordform.analysis
            if not analysis:
                continue
            analysis_tags = analysis.tag_set()

            if "+V" in self.new_tags and r.is_lemma and "+V" in analysis_tags:
                words.append(r)
            if "+N" in self.new_tags and r.is_lemma and "+N" in analysis_tags:
                words.append(r)
            if settings.DEFAULT_PHRASE_TRANSLATE_CHECK(self.new_tags):
                words.append(r)

        return words

    def _generate_inflected_results(self) -> list[_EipResult]:
        """
        From the results, sort out the inflectable wordforms, then inflect them
        using the new set of tags.
        Return the inflected wordforms.
        """

        words = self._collect_non_inflected_results()

        orig_tags_starting_with_plus: list[str] = []
        tags_ending_with_plus: list[str] = []
        for t in self.new_tags:
            if t.startswith("+"):
                orig_tags_starting_with_plus.append(t)
            else:
                tags_ending_with_plus.append(t)

        results = []
        for word in words:
            # This is sometimes mutated
            tags_starting_with_plus = orig_tags_starting_with_plus[:]

            noun_tags = []
            if "+N" in word.wordform.analysis.tag_set():
                noun_tags = [
                    tag
                    for tag in word.wordform.analysis.suffix_tags
                    if tag in source_noun_tags
                ]
                if "+N" in tags_starting_with_plus:
                    tags_starting_with_plus.remove("+N")
                if "+Der/Dim" in tags_starting_with_plus:
                    # noun tags need to be repeated in this case
                    insert_index = tags_starting_with_plus.index("+Der/Dim") + 1
                    tags_starting_with_plus[insert_index:insert_index] = noun_tags

            analysis = RichAnalysis(
                (
                    tags_ending_with_plus,
                    word.wordform.text,
                    noun_tags + tags_starting_with_plus,
                )
            )

            generated_wordforms = analysis.generate()
            for w in generated_wordforms:
                results.append(
                    _EipResult(
                        original_result=word, inflected_text=w, analysis=analysis
                    )
                )
        return results
