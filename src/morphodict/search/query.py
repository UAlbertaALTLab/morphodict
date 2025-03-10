import unicodedata
from enum import Enum
from typing import Optional

import marshmallow.fields

from morphodict.search import runner
from morphodict.search.util import to_sro_circumflex


class CvdSearchType(Enum):
    # Do not use cosine vector distance at all.
    OFF = 0

    # Add some CVD-based results
    RETRIEVAL = 1
    DEFAULT = RETRIEVAL

    # Only use cosine vector distance, for both retrieval and ranking. Helpful
    # for inspecting how CVD performs, but not generally useful because only
    # returns results for English-language inputs.
    EXCLUSIVE = 2

    def should_do_search(self):
        return self != CvdSearchType.OFF


def treat_query(query_string):
    # Whitespace won't affect results, but the FST can't deal with it:
    query_string = query_string.strip()
    # All internal text should be in NFC form --
    # that is, all characters that can be composed are composed.
    query_string = unicodedata.normalize("NFC", query_string)

    query_string = query_string.lower()
    query_string = query_string.replace("7", "ʔ")
    query_string = to_sro_circumflex(query_string)
    return query_string


class Query:
    BOOL_KEYS = ["verbose", "auto", "espt", "nofetch", "wn"]

    def __init__(self, query_string):
        self.raw_query_string = query_string

        query_string = treat_query(query_string)

        self.query_terms = []

        for token in query_string.split():
            # Whether this token has been used by some interpretation step
            consumed = False

            if ":" in token:
                user_key, value = token.split(":", 1)

                if user_key in Query.BOOL_KEYS:
                    consumed = True
                    setattr(self, user_key, value in marshmallow.fields.Boolean.truthy)
                elif user_key == "cvd":
                    consumed = True

                    try:
                        self.cvd = runner.CvdSearchType(int(value))
                    except ValueError:
                        for t in runner.CvdSearchType:
                            if value == t.name.lower():
                                self.cvd = t
                                break

            if not consumed:
                self.query_terms.append(token)

        self.is_valid = self.query_string != ""

    @property
    def query_string(self):
        return " ".join(self.query_terms)

    def replace_query(self, new_query):
        """
        Inflected phrase search discards functional words like "they" using this method
        Does not affect flags
        """
        query_string = treat_query(new_query)
        self.query_terms = query_string.split()

    def __repr__(self) -> str:
        return f"<Query {self.raw_query_string!r}>"

    is_valid: bool
    verbose: Optional[bool] = None
    auto: Optional[bool] = None
    cvd: Optional[CvdSearchType] = None
    espt: Optional[bool] = None
    nofetch: Optional[bool] = None
    wn: Optional[bool] = None
