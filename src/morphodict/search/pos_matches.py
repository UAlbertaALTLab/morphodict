from morphodict.search.core import SearchResults
from morphodict.phrase_translate.fst import source_phrase_analyses
from morphodict.analysis import rich_analyze_relaxed


def find_pos_matches(search_results: SearchResults) -> None:
    analyzed_query = AnalyzedQuery(search_results.internal_query)
    # print(search_results.verbose_messages["new_tags"])

    if len(search_results.verbose_messages) <= 1:
        return
    tags = search_results.verbose_messages[1].get("tags")
    [pos_match(result, tags) for result in search_results.unsorted_results()]


def pos_match(result, tags):
    """
    Returns an int value based on how closely related the search result and query term are
    The higher the value, the more related
    If they aren't related or aren't analyzable, return 0
    """
    if not tags:
        result.pos_match = 0
        return
    if not result.wordform.raw_analysis:
        result.pos_match = 0
        return

    result_tags = result.wordform.raw_analysis[2]
    query_tags = tags

    max = min(len(result_tags), len(query_tags))
    i = 0
    j = 0
    while j < max:
        if result_tags[j] == query_tags[j]:
            i += 1 / (j + 1)
        j += 1
    result.pos_match = i
    return


class AnalyzedQuery:
    """
    A structured object holding pieces of, and info about, a phrase query.
    """

    def __init__(self, query: str):
        self.query = query
        self.has_tags = False
        self.filtered_query = None
        self.tags = None
        self.analysis = []
        phrase_analyses = rich_analyze_relaxed(query)

        if len(phrase_analyses) == 1:
            phrase_analysis = phrase_analyses[0]

            self.analysis = phrase_analysis.suffix_tags
            if phrase_analysis:
                self.has_tags = True

        else:
            phrase_analyses = source_phrase_analyses(query)
            if phrase_analyses:
                phrase_analysis = phrase_analyses[0]
                self.has_tags = True
                split_tags = (
                    phrase_analysis.split()[1].split("+")
                    if len(phrase_analysis.split()) > 1
                    else []
                )
                analysis = []
                for tag in split_tags:
                    if not tag:
                        continue
                    tag = "+" + tag
                    analysis.append(tag)
                self.analysis = analysis

    def __repr__(self):
        return f"<AnalyzedQuery {self.__dict__!r}>"
