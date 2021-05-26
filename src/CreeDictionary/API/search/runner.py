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
from CreeDictionary.API.search.util import first_non_none_value
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from CreeDictionary.shared import expensive
from CreeDictionary.utils.types import cast_away_optional

crkeng_tag_dict = {
    "+Prt": ("PV/ki+", "+Ind"),  # Preterite aka simple past
    "+Cond": ("+Fut", "+Cond"),  # Future conditional
    "+Imm": ("+Imp", "+Imm"),  # Immediate imperative
    "+Del": ("+Imp", "+Del"),  # Delayed imperative
    "+Fut": ("PV/wi+", "+Ind"), # Future
    # "+Fut": "PV/wi+",  # Also accept PV/wi without indicative as future
    # Note that these crk features as disjoint, but both are needed for the eng feature
    "+Def": ("PV/ka+", "+Ind"),
    "+Inf": ("PV/ka+", "+Cnj"),
    # "+Inf": ("PV/ta+", "+Cnj")  # future definite
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

    if search_run.query.eip:
        analyzed_query = PhraseAnalyzedQuery(search_run.query.query_string)
        new_tags = []
        if analyzed_query.has_tags:
            search_run.query.replace_query(analyzed_query.filtered_query)
            for tag in analyzed_query.tags:
                if tag in crkeng_tag_dict:
                    for i in crkeng_tag_dict[tag]:
                        new_tags.append(i)
                else:
                    new_tags.append(tag)

        search_run.add_verbose_message(dict(
            filtered_query=analyzed_query.filtered_query,
            tags=analyzed_query.tags,
            new_tags=new_tags
        ))

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

    verbs = []
    for r in search_run.serialized_presentation_results():
        if r["lemma_wordform"]["pos"] == "V":
            verbs.append(r["wordform_text"])

    prefix_tags = ""
    for tag in new_tags:
        if not tag.startswith('+'):
            prefix_tags += tag

    affix_tags = ""
    for tag in new_tags:
        if tag.startswith('+'):
            affix_tags += tag

    results = []
    for verb in verbs:
        text = prefix_tags + verb + affix_tags
        result = expensive.strict_generator.lookup(text)
        if result:
            results.append(result)
    print(results)

    search_run.add_verbose_message(dict(results=results))
    return search_run
