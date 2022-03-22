from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from morphodict.analysis import rich_analyze_relaxed


def find_pos_matches(search_run: SearchRun) -> None:

    analyzed_query = AnalyzedQuery(
                search_run.internal_query
            )

    for result in search_run.unsorted_results():
        result.pos_match = pos_match(result, analyzed_query)


def pos_match(result, analyzed_query):
    """
    Returns an int value based on how closely related the search result and query term are
    The higher the value, the more related
    If they aren't related or aren't analyzable, return 0
    """
    if not analyzed_query.has_tags:
        return 0
    if not result.wordform.raw_analysis:
        return 0

    result_tags = result.wordform.raw_analysis[2]
    query_tags = list(analyzed_query.analysis)

    max = min(len(result_tags), len(query_tags))
    i = 0
    j = 0
    while j < max:
        if result_tags[i] == query_tags[i]:
            i += 1
        j += 1
    return i



class AnalyzedQuery:
    """A structured object holding pieces of, and info about, a phrase query.

    >>> AnalyzedQuery("they swam").filtered_query
    'swim'
    >>> AnalyzedQuery("they swam").has_tags
    True
    >>> AnalyzedQuery("they swam").tags
    ['+V', '+AI', '+Prt', '+3Pl']
    >>> AnalyzedQuery("excellent").has_tags
    False
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
            phrase_analyses = eng_phrase_to_crk_features_fst()[query]
            if phrase_analyses:
                phrase_analysis = phrase_analyses[0].decode('utf-8')
                self.has_tags = True
                split_tags = phrase_analysis.split()[1].split('+') if len(phrase_analysis.split()) > 1  else []
                analysis = []
                for tag in split_tags:
                    if not tag:
                        continue
                    tag = "+" + tag
                    analysis.append(tag)
                self.analysis = analysis


    def __repr__(self):
        return f"<PhraseAnalyzedQuery {self.__dict__!r}>"
