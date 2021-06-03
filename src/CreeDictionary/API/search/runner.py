from dataclasses import dataclass

from CreeDictionary.API.models import Wordform
from CreeDictionary.API.search.affix import (
    do_source_language_affix_search,
    do_target_language_affix_search,
    query_would_return_too_many_results,
)
from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.API.search.cvd_search import do_cvd_search
from CreeDictionary.API.search.eip import PhraseAnalyzedQuery
from CreeDictionary.API.search.lookup import fetch_results
from CreeDictionary.API.search.query import CvdSearchType
from CreeDictionary.API.search.types import Result
from CreeDictionary.API.search.util import first_non_none_value
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from CreeDictionary.shared import expensive
from CreeDictionary.utils import get_modified_distance
from CreeDictionary.utils.types import cast_away_optional

crkeng_tag_dict = {
    "+Prt": ("PV/ki+", "+Ind"),  # Preterite aka simple past
    "+Cond": ("+Fut", "+Cond"),  # Future conditional
    "+Imm": ("+Imp", "+Imm"),  # Immediate imperative
    "+Del": ("+Imp", "+Del"),  # Delayed imperative
    "+Fut": ("PV/wi+", "+Ind"),  # Future
    # "+Fut": "PV/wi+",  # Also accept PV/wi without indicative as future
    # Note that these crk features as disjoint, but both are needed for the eng feature
    "+Def": ("PV/ka+", "+Ind"),
    "+Inf": ("PV/ka+", "+Cnj"),
    # "+Inf": ("PV/ta+", "+Cnj")  # future definite
    "+Dim": ("+Der/Dim",),
}


def search(
    *, query: str, include_affixes=True, include_auto_definitions=False
) -> SearchRun:
    """
    Perform an actual search, using the provided options.

    This class encapsulates the logic of which search methods to try, and in
    which order, to build up results in a SearchRun.
    """
    search_run = SearchRun(
        query=query, include_auto_definitions=include_auto_definitions
    )

    new_tags = []
    if search_run.query.eip:
        analyzed_query = PhraseAnalyzedQuery(search_run.query.query_string)
        if analyzed_query.has_tags:
            search_run.query.replace_query(analyzed_query.filtered_query)
            for tag in analyzed_query.tags:
                if tag in crkeng_tag_dict:
                    for i in crkeng_tag_dict[tag]:
                        new_tags.append(i)
                else:
                    new_tags.append(tag)

        search_run.add_verbose_message(
            dict(
                filtered_query=analyzed_query.filtered_query,
                tags=analyzed_query.tags,
                new_tags=new_tags,
            )
        )

    cvd_search_type = cast_away_optional(
        first_non_none_value(search_run.query.cvd, default=CvdSearchType.DEFAULT)
    )

    if cvd_search_type == CvdSearchType.EXCLUSIVE:
        do_cvd_search(search_run)
        return search_run

    fetch_results(search_run)

    if include_affixes and not query_would_return_too_many_results(
        search_run.internal_query
    ):
        do_source_language_affix_search(search_run)
        do_target_language_affix_search(search_run)

    if cvd_search_type.should_do_search():
        do_cvd_search(search_run)

    inflected_results = generate_inflected_results(new_tags, search_run)
    print(inflected_results)

    # FIXME: get all wordforms in a single query?
    for result in inflected_results:
        exactly_matched_wordform = Wordform.objects.filter(
            text=result.inflected_text, lemma=result.original_result.wordform
        ).first()

        if exactly_matched_wordform:
            search_run.remove_result(result.original_result)
            search_run.add_result(
                result.original_result.create_related_result(
                    exactly_matched_wordform, is_eip_result=True
                )
            )

    return search_run


@dataclass
class EipResult:
    inflected_text: str
    original_result: Result


def generate_inflected_results(tags, search_run) -> list[EipResult]:
    """
    Of the results, sort out the verbs, then inflect them
    using the new set of tags.
    Return the inflected verbs.
    """

    words = []
    for r in search_run.unsorted_results():
        if "+V" in tags and r.is_lemma and r.lemma_wordform.pos == "V":
            words.append(r)
        if "+N" in tags and r.is_lemma and r.lemma_wordform.pos == "N":
            words.append(r)

    tags_starting_with_plus = []
    tags_ending_with_plus = []
    for t in tags:
        (
            tags_starting_with_plus if t.startswith("+") else tags_ending_with_plus
        ).append(t)

    results = []
    for word in words:
        noun_tags = ""
        if 'N' in word.wordform.inflectional_category:
            noun_tags = get_noun_tags(word.wordform.inflectional_category)
            if '+N' in tags_starting_with_plus:
                tags_starting_with_plus.remove('+N')
            if "+Der/Dim" in tags_starting_with_plus:
                # noun tags need to be repeated in this case
                index = tags_starting_with_plus.index("+Der/Dim")
                tags_starting_with_plus.insert(index+1, noun_tags)

        text = (
            "".join(tags_ending_with_plus)
            + word.lemma_wordform.text
            + noun_tags
            + "".join(tags_starting_with_plus)
        )

        generated_wordforms = expensive.strict_generator.lookup(text)
        for w in generated_wordforms:
            results.append(
                EipResult(
                    original_result=word,
                    inflected_text=w,
                )
            )

        # noun tags are specific to each word
        if noun_tags in tags_starting_with_plus:
            tags_starting_with_plus.remove(noun_tags)

    return results


def get_noun_tags(inflectional_category):
    noun_tags = ""
    for c in inflectional_category:
        if c == '-':
            return noun_tags
        noun_tags += '+' + c

    return noun_tags
