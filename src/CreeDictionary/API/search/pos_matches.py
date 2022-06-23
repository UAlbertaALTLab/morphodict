from CreeDictionary.API.search.core import SearchRun
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
from morphodict.analysis import rich_analyze_relaxed


def find_pos_matches(search_run: SearchRun) -> None:

    analyzed_query = AnalyzedQuery(search_run.internal_query)
    # print(search_run.verbose_messages["new_tags"])
    print(analyzed_query)

    if len(search_run.verbose_messages) <= 1:
        tags = analyzed_query.analysis
    else:
        tags = search_run.verbose_messages[1].get("tags")
    [pos_match(result, tags) for result in search_run.unsorted_results()]


def pos_match(result, tags):
    """
    Returns an int value based on how closely related the search result and query term are
    The higher the value, the more related
    If they aren't related or aren't analyzable, return 0
    """
    if not tags:
        result.pos_match = 0
        print('returned at 27')
        return
    if result.wordform.raw_analysis:
        result_tags = result.wordform.raw_analysis[2]
    elif result.wordform.linguist_info['pos']:
        result_tags = ["+" + r for r in result.wordform.linguist_info['pos']]
    else:
        result.pos_match = 0
        return

    query_tags = tags
    print("TAG TYPE:", type(result_tags))

    if isinstance(result_tags, list):
        result.pos_match = calculate_pos_match(result_tags, query_tags)
        return
    else:
        max = 0
        for tag_list in query_tags:
            pos_match = calculate_pos_match(result_tags, tag_list)
            if pos_match > max:
                max = pos_match
        result.pos_match = max
        return


def calculate_pos_match(result_tags, query_tags):
    max = min(len(result_tags), len(query_tags))
    i = 0
    j = 0
    while j < max:
        if result_tags[j] == query_tags[j]:
            i += 1 / (j + 1)
        j += 1
    return i

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
            phrase_analyses = eng_phrase_to_crk_features_fst()[query]
            if phrase_analyses:
                phrase_analysis = phrase_analyses[0].decode("utf-8")
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
        return f"<PhraseAnalyzedQuery {self.__dict__!r}>"
