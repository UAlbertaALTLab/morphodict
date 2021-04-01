from utils import Language, get_modified_distance
from .types import SearchResult
from ..models import wordform_cache


def sort_search_result(
    res_a: SearchResult, res_b: SearchResult, user_query: str
) -> float:
    """
    determine how we sort search results.

    :return:   0: does not matter;
              >0: res_a should appear after res_b;
              <0: res_a should appear before res_b.
    """

    if res_a.matched_by is Language.CREE and res_b.matched_by is Language.CREE:
        # both from cree
        a_dis = get_modified_distance(user_query, res_a.matched_cree)
        b_dis = get_modified_distance(user_query, res_b.matched_cree)
        difference = a_dis - b_dis
        if difference:
            return difference

        # Both results are EXACTLY the same form!
        # Further disambiguate by checking if one is the lemma.
        if res_a.is_lemma and res_b.is_lemma:
            return 0
        elif res_a.is_lemma:
            return -1
        elif res_b.is_lemma:
            return 1
        else:
            # Somehow, both forms exactly match the user query and neither
            # is a lemma?
            return 0

    # todo: better English sort
    elif res_a.matched_by is Language.CREE:
        # a from cree, b from English
        return -1
    elif res_b.matched_by is Language.CREE:
        # a from English, b from Cree
        return 1
    else:

        # both from English
        a_in_rankings = res_a.matched_cree in wordform_cache.MORPHEME_RANKINGS
        b_in_rankings = res_b.matched_cree in wordform_cache.MORPHEME_RANKINGS

        if a_in_rankings and not b_in_rankings:
            return -1
        elif not a_in_rankings and b_in_rankings:
            return 1
        elif not a_in_rankings and not b_in_rankings:
            return 0
        else:  # both in rankings
            return (
                wordform_cache.MORPHEME_RANKINGS[res_a.matched_cree]
                - wordform_cache.MORPHEME_RANKINGS[res_b.matched_cree]
            )
