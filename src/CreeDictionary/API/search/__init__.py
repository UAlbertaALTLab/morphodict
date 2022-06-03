from .runner import search


def search_with_affixes(
    query: str, include_auto_definitions=False, inflect_english_phrases=False
):
    """
    Search for wordforms matching:
     - the wordform text
     - the definition keyword text
     - affixes of the wordform text
     - affixes of the definition keyword text
    """

    return search(
        query=query,
        include_auto_definitions=include_auto_definitions,
        inflect_english_phrases=inflect_english_phrases,
    )


def simple_search(
    query: str, include_auto_definitions=False, inflect_english_phrases=False
):
    """
    Search, trying to match full wordforms or keywords within definitions.

    Does NOT try to match affixes!
    """

    return search(
        query=query,
        include_affixes=False,
        include_auto_definitions=include_auto_definitions,
        inflect_english_phrases=inflect_english_phrases,
    ).serialized_presentation_results()
