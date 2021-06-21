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


class WordformQuery(TypedDict):
    text: str
    lemma__slug: str
    raw_analysis: str


def definition_to_cvd_key(d: Definition) -> CvdKey:
    """Return a string that can be used for keying the given definition"""
    return cast(
        CvdKey,
        json.dumps(
            [
                # Every lemma has a stable unique identifier
                d.wordform.lemma.slug,
                # These next two should fields should identify non-lemma wordforms
                d.wordform.text,
                # FIXME: use smushed for faster lookups?
                d.wordform.raw_analysis,
                # This is just a disambiguator so we can have multiple definitions
                # for the same word in a vector file without conflict.
                d.id,
            ],
            ensure_ascii=False,
        ),
    )


def cvd_key_to_wordform_query(s: CvdKey) -> Optional[WordformQuery]:
    """Return kwargs for Wordform.objects.filter() to retrieve wordform

    While unambiguous, likely too slow for querying.
    """
    key_list = json.loads(s)
    if len(key_list) != 4:
        logger.error(
            "Unable to parse cvd key; the format may have changed, run builddefinitionvectors?"
        )
        return None

    slug, text, raw_analysis, _ = key_list
    return {
        "text": text,
        "lemma__slug": slug,
        "raw_analysis": raw_analysis,
    }


def wordform_query_matches(query: WordformQuery, wordform: Wordform):
    return (
        wordform.text == query["text"]
        and wordform.raw_analysis == query["raw_analysis"]
        and wordform.lemma.slug == query["lemma__slug"]
    )
