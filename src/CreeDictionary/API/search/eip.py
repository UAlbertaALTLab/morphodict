"""
EIP: English Inflected Phrase search
"""
import logging
import re
from dataclasses import dataclass

from CreeDictionary.API.models import Wordform
from CreeDictionary.API.search.eip_crk import (
    get_noun_tags,
    verb_tag_map,
    noun_tag_map,
)
from CreeDictionary.API.search.types import Result
from morphodict.analysis.tag_map import UnknownTagError
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from morphodict.analysis import strict_generator

logger = logging.getLogger(__name__)


@dataclass
class _EipResult:
    """Tiny class to connect inflected text to original search result"""

    inflected_text: str
    analysis: str
    original_result: Result


class EipSearch:
    """An English Inflected Phrase search.

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
                self.search_run.add_verbose_message(dict(eip_analysis_error=repr(e)))
                return

        self.search_run.query.replace_query(analyzed_query.filtered_query)
        self.query_analyzed_ok = True

        self.search_run.add_verbose_message(
            dict(
                filtered_query=analyzed_query.filtered_query,
                tags=analyzed_query.tags,
                new_tags=self.new_tags,
            )
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
                # inflected form not found in DB, so create a synthetic one.
                # This is unlikely to occur for Plains Cree, as it would require
                # the EIP search to produce a valid analysis not covered by any
                # paradigm file.
                #
                # Note: would not have auto-translations since those are
                # currently only available for wordforms that were previously
                # saved in the DB.
                lemma = result.original_result.lemma_wordform

                wordform = Wordform(
                    text=result.inflected_text,
                    lemma=lemma,
                    inflectional_category=lemma.inflectional_category,
                    pos=lemma.pos,
                    stem=lemma.stem,
                    analysis=result.analysis,
                )

            # if there are multiple inflections for the same original result, we
            # may already have removed it
            if self.search_run.has_result(result.original_result):
                self.search_run.remove_result(result.original_result)

            self.search_run.add_result(
                result.original_result.create_related_result(
                    wordform,
                    is_eip_result=True,
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
            if "+V" in self.new_tags and r.is_lemma and r.lemma_wordform.pos == "V":
                words.append(r)
            if "+N" in self.new_tags and r.is_lemma and r.lemma_wordform.pos == "N":
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

            noun_tags = ""
            if "N" in word.wordform.inflectional_category:
                noun_tags = get_noun_tags(word.wordform.inflectional_category)
                if "+N" in tags_starting_with_plus:
                    tags_starting_with_plus.remove("+N")
                if "+Der/Dim" in tags_starting_with_plus:
                    # noun tags need to be repeated in this case
                    index = tags_starting_with_plus.index("+Der/Dim")
                    tags_starting_with_plus.insert(index + 1, noun_tags)

            text = (
                "".join(tags_ending_with_plus)
                + word.lemma_wordform.text
                + noun_tags
                + "".join(tags_starting_with_plus)
            )

            generated_wordforms = strict_generator().lookup(text)
            for w in generated_wordforms:
                results.append(
                    _EipResult(original_result=word, inflected_text=w, analysis=text)
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
            add_verbose_message({"phrase_analyses": phrase_analyses})

        if len(phrase_analyses) != 1:
            return

        phrase_analysis = phrase_analyses[0]
        if "+?" in phrase_analysis:
            return

        match = PHRASE_ANALYSIS_OUTPUT_RE.fullmatch(phrase_analysis)
        if not match:
            return

        self.filtered_query = match["query"]
        self.has_tags = True
        self.tags = ["+" + t for t in match["tags"].split("+") if t]

    def __repr__(self):
        return f"<PhraseAnalyzedQuery {self.__dict__!r}>"
