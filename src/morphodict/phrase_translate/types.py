import re
from morphodict.phrase_translate.fst import source_phrase_analyses

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
        self.filtered_query: str | None = None
        self.tags = None
        phrase_analyses: list[str] = source_phrase_analyses(query)

        if add_verbose_message:
            add_verbose_message(phrase_analyses=phrase_analyses)

        if len(phrase_analyses) != 1:
            return

        phrase_analysis = phrase_analyses[0]
        if "+?" in phrase_analysis:
            return

        if not (match := PHRASE_ANALYSIS_OUTPUT_RE.fullmatch(phrase_analysis)):
            return

        self.filtered_query = match["query"]
        self.has_tags = True
        self.tags = ["+" + t for t in match["tags"].split("+") if t]

    def __repr__(self):
        return f"<PhraseAnalyzedQuery {self.__dict__!r}>"
