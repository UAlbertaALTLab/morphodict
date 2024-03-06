"""
ESPT: English simple phrase translation
"""

import logging
import re
from dataclasses import dataclass

from CreeDictionary.API.search.espt_crk import (
    verb_tag_map,
    noun_tag_map,
    crk_noun_tags,
)
from CreeDictionary.API.search.types import Result
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from morphodict.analysis import RichAnalysis
from morphodict.analysis.tag_map import UnknownTagError
from morphodict.lexicon.models import Wordform

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

    def __init__(self, search_run):
        self.search_run = search_run
        self.query_analyzed_ok = False

    def analyze_query(self):
        """Analyze this search’s search_run query, possibly updating it.

        If the phrase-parsing FST returns an analysis, e.g., “ crawls
        +V+AI+Prt+3Pl” for “they crawled”, then the tags are saved for
        inflecting search results later, and the query is updated to only
        include content words, e.g., “they crawled” → “crawls”.
        """
        self.new_tags = []
        analyzed_query = PhraseAnalyzedQuery(
            self.search_run.internal_query,
            add_verbose_message=self.search_run.add_verbose_message,
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
                self.search_run.add_verbose_message(espt_analysis_error=repr(e))
                return

            self.search_run.query.replace_query(analyzed_query.filtered_query)
            self.query_analyzed_ok = True

        self.search_run.add_verbose_message(
            filtered_query=analyzed_query.filtered_query,
            tags=analyzed_query.tags,
            new_tags=self.new_tags,
        )

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
            if self.search_run.has_result(result.original_result):
                self.search_run.remove_result(result.original_result)

            self.search_run.add_result(
                result.original_result.create_related_result(
                    wordform,
                    is_espt_result=True,
                )
            )

    def _generate_inflected_results(self) -> list[_EipResult]:
        """
        From the results, sort out the inflectable wordforms, then inflect them
        using the new set of tags.
        Return the inflected wordforms.
        """

        words = []
        for r in self.search_run.unsorted_results():
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
                    if tag in crk_noun_tags
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


# e.g., " swim +V+AI+Prt+3Pl"
PHRASE_ANALYSIS_OUTPUT_RE = re.compile(
    r"""
                        \s*             # leading blank space(s) from flag diacritics
                        (?P<query>.*)
                        \s
                        (?P<tags>\+[^\ ]+)
                    """,
    re.VERBOSE,
)


class PhraseAnalyzedQuery:
    """A structured object holding pieces of, and info about, a phrase query.

    >>> PhraseAnalyzedQuery("they swam").filtered_query
    'swim'
    >>> PhraseAnalyzedQuery("they swam").has_tags
    True
    >>> PhraseAnalyzedQuery("they swam").tags
    ['+V', '+AI', '+Prt', '+3Pl']
    >>> PhraseAnalyzedQuery("excellent").has_tags
    False
    """

    def __init__(self, query: str, add_verbose_message=None):
        self.query = query
        self.has_tags = False
        self.filtered_query = None
        self.tags = None
        phrase_analyses: list[str] = [
            r.decode("UTF-8") for r in eng_phrase_to_crk_features_fst()[query]
        ]

        if add_verbose_message:
            add_verbose_message(phrase_analyses=phrase_analyses)

        if len(phrase_analyses) != 1:
            return

        phrase_analysis = phrase_analyses[0]
        if "+?" in phrase_analysis:
            return

        if not (match := PHRASE_ANALYSIS_OUTPUT_RE.fullmatch(phrase_analysis)):
            return

        self.filtered_query = match["query"]
        self.has_tags = True
        self.tags = ["+" + t for t in match["tags"].split("+") if t]

    def __repr__(self):
        return f"<PhraseAnalyzedQuery {self.__dict__!r}>"
