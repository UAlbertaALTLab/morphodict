"""
We build definition vectors so that we can find relevant definitions, and then
later display the associated wordforms.

This file has functions to turn definitions into string keys that:
 1. Are unique per definition, so we can save multiple definitions per wordform
    into a KeyedVector
 2. Also refer unambiguously to a single wordform.
"""

import json
import logging
from typing import TypedDict, cast, Optional

from morphodict.lexicon.models import Wordform, Definition

logger = logging.getLogger(__name__)

CvdKey = str


class WordformQuery(TypedDict, total=False):
    text: str
    lemma__slug: str
    raw_analysis: Optional[str]
    raw_analysis__isnull: Optional[bool]


def definition_to_cvd_key(d: Definition) -> CvdKey:
    """Return a string that can be used for keying the given definition"""
    return cast(
        CvdKey,
        json.dumps(
            [
                # Every lemma has a stable unique identifier
                getattr(d.wordform.lemma, "slug"),
                # These next two should fields should identify non-lemma wordforms
                d.wordform.text,
                d.wordform.raw_analysis,
                # This is just a disambiguator so we can have multiple definitions
                # for the same word in a vector file without conflict.
                d.id,
            ],
            ensure_ascii=False,
        ),
    )


def cvd_key_to_wordform_query(s: CvdKey) -> WordformQuery:
    """Return kwargs for Wordform.objects.filter() to retrieve wordform

    While unambiguous, requires care to use for bulk queries. See
    do_cvd_search() for an example use.
    """
    slug, text, raw_analysis, _ = json.loads(s)
    ret: WordformQuery = {
        "text": text,
        "lemma__slug": slug,
    }
    if raw_analysis:
        ret["raw_analysis"] = raw_analysis
    else:
        ret["raw_analysis__isnull"] = True
    return ret


def wordform_query_matches(query: WordformQuery, wordform: Wordform):
    return (
        wordform.text == query["text"]
        and (
            ("raw_analysis" in query and wordform.raw_analysis == query["raw_analysis"])
            or ("raw_analysis__isnull" in query and wordform.raw_analysis is None)
        )
        and getattr(wordform.lemma, "slug") == query["lemma__slug"]
    )
