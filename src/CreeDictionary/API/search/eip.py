# EIP: English Inflected Phrase search
from CreeDictionary.phrase_translate.translate import eng_phrase_to_crk_features_fst
import re

# e.g., " swim +V+AI+Prt+3Pl"
TAG_RE = re.compile(
    r"""
                        \s*             # leading blank space(s) from flag diacritics
                        (?P<query>.*)
                        \s
                        (?P<tags>\+[^\ ]+)
                    """,
    re.VERBOSE,
)


class PhraseAnalyzedQuery:
    def __init__(self, query: str):
        self.query = query
        self.has_tags = False
        self.filtered_query = None
        self.tags = None
        phrase_analysis = [
            r.decode("UTF-8") for r in eng_phrase_to_crk_features_fst()[query]
        ]

        if len(phrase_analysis) != 1:
            return

        phrase_analysis = phrase_analysis[0]
        if "+?" in phrase_analysis:
            return

        match = TAG_RE.fullmatch(phrase_analysis)
        if not match:
            return

        self.filtered_query = match["query"]
        self.has_tags = True
        self.tags = ["+" + t for t in match["tags"].split("+") if t]
