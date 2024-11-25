import itertools
import logging

from morphodict.search.core import SearchResults, Query
from morphodict.search.types import Result
from morphodict.cvd import (
    definition_vectors,
    google_news_vectors,
    extract_keyed_words,
    vector_for_keys,
    DefinitionVectorsNotFoundException,
)
from morphodict.cvd.definition_keys import (
    cvd_key_to_wordform_query,
    wordform_query_matches,
)
from morphodict.lexicon.models import Wordform

logger = logging.getLogger(__name__)


def do_cvd_search(query: Query, search_results: SearchResults):
    """Use cosine vector distance to add results to the search run.

    Keywords from the query string are turned into vectors from Google News,
    added together, and then compared against pre-computed definition vectors.
    """
    keys = extract_keyed_words(query.query_string, google_news_vectors())
    if not keys:
        return

    search_results.add_verbose_message(cvd_extracted_keys=keys)
    query_vector = vector_for_keys(google_news_vectors(), keys)

    try:
        closest = definition_vectors().similar_by_vector(query_vector, 50)
    except DefinitionVectorsNotFoundException:
        logger.exception("Definition Vectors Not Found")
        return

    wordform_queries = [
        cvd_key_to_wordform_query(similarity) for similarity, weight in closest
    ]
    similarities = [similarity for cvd_key, similarity in closest]

    # Get all possible wordforms in one big query. We will select more than we
    # need, then filter it down later, but this will have to do until we get
    # better homonym handling.
    wordform_results = Wordform.objects.filter(
        text__in=set(wf["text"] for wf in wordform_queries)
    )

    # Now match back up
    wordforms_by_text = {
        text: list(wordforms)
        for text, wordforms in itertools.groupby(wordform_results, key=lambda x: x.text)
    }

    for similarity, wordform_query in zip(similarities, wordform_queries):
        # gensim uses the terminology, similarity = 1 - distance. Its
        # similarity is a number from 0 to 1, with more similar items having
        # similarity closer to 1. A distance should be small for things that
        # are close together.
        distance = 1 - similarity

        wordforms_for_query = wordforms_by_text.get(wordform_query["text"], None)
        if wordforms_for_query is None:
            logger.warning(
                f"Wordform {wordform_query['text']} not found in CVD; mismatch between definition vector model file and definitions in database?"
            )
        else:
            for wf in wordforms_for_query:
                if wordform_query_matches(wordform_query, wf):
                    search_results.add_result(Result(wf, cosine_vector_distance=distance))
