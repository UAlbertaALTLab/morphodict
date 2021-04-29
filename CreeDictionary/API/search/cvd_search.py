import itertools
import operator
from functools import reduce

from django.db.models import Q

from API.models import Wordform
from API.search.core import SearchRun
from API.search.types import Result
from cvd import (
    definition_vectors,
    google_news_vectors,
    extract_keyed_words,
    vector_for_keys,
)
from cvd.definition_keys import cvd_key_to_wordform_query, wordform_query_matches


def do_cvd_search(search_run: SearchRun):
    keys = extract_keyed_words(search_run.query.query_string, google_news_vectors())
    if not keys:
        return

    query_vector = vector_for_keys(google_news_vectors(), keys)

    closest = definition_vectors().similar_by_vector(query_vector, 50)
    wordform_queries = [
        cvd_key_to_wordform_query(similarity) for similarity, weight in closest
    ]
    similarities = [similarity for cvd_key, similarity in closest]

    # Get all wordforms in one big OR query
    wordform_results = Wordform.objects.filter(
        reduce(
            operator.or_,
            (Q(**q) for q in wordform_queries),
        )
    ).order_by("text")

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

        for wf in wordforms_by_text[wordform_query["text"]]:
            if wordform_query_matches(wordform_query, wf):
                search_run.add_result(Result(wf, cosine_vector_distance=distance))
