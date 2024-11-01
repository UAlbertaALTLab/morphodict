import logging
import re
from functools import cache
from os import fspath

from django.conf import settings
from gensim.models import KeyedVectors

from morphodict.lexicon import MORPHODICT_LEXICON_RESOURCE_DIR
from morphodict.relabelling import LABELS

logger = logging.getLogger(__name__)

shared_vector_model_dir = MORPHODICT_LEXICON_RESOURCE_DIR / "vector_models"


language_specific_vector_model_dir = settings.BASE_DIR / "resources" / "vector_models"


# Bump this value when changing the format used to store the keys, so that
# loading keyedvector files from one format doesn’t crash code expecting
# another.
CVD_KEY_FORMAT = 2


def _load_vectors(path):
    return KeyedVectors.load(fspath(path), mmap="r")


@cache
def google_news_vectors():
    return _load_vectors(shared_vector_model_dir / "news_vectors.kv")


class DefinitionVectorsNotFoundException(Exception):
    def __init__(self):
        super().__init__(
            "Definition vectors not found. Not able to use cosine vector distance for search. Run `manage.py builddefinitionvectors`."
        )


def definition_vectors_path():
    filename = f"definitions_v{CVD_KEY_FORMAT}.kv"
    if settings.USE_TEST_DB:
        filename = f"test_db_definitions_v{CVD_KEY_FORMAT}.kv"
    return language_specific_vector_model_dir / filename


@cache
def definition_vectors():
    try:
        return _load_vectors(definition_vectors_path())

    except FileNotFoundError:
        raise DefinitionVectorsNotFoundException


def preload_models():
    try:
        definition_vectors()
    except DefinitionVectorsNotFoundException:
        logger.exception("")

    # doing a similarity search compares against every other vector, so by doing
    # similar_by_key for any key at all, we preload the entire vector model into
    # memory.
    google_news_vectors().similar_by_key("hello")


# Implementation from https://stackoverflow.com/a/48027864/14558 which cites
# https://www.peterbe.com/plog/fastest-way-to-uniquify-a-list-in-python-3.6
# which cites a tweet of Raymond Hettinger
def uniq(l: list) -> list:
    """Return unique elements from l"""
    return list(dict.fromkeys(l))


# Note: The computation of this vector for definition is memoized by the builddefinitionvectors django command.
# They are not live-computed.  If there are changes to this code, please make sure to re-run builddefinitionvectors
# as a command.
def vector_for_keys(keyed_vectors, keys: list[str]):
    """Return the sum of vectors in keyed_vectors for the given keys"""
    if not keys:
        raise ValueError("keys cannot be empty")

    return keyed_vectors[keys].sum(axis=0)


RE_PUNCTUATION = re.compile(r'[!,.\[\]\(\)\{\};:"/\?]+')


def extract_keyed_words(query: str, keys, already_warned=None, analysis=[]):
    """Split query into a list of words that occur in keys

    already_warned is an optional set, used to reduce debug log verbosity
    """
    ret = []

    query = query.lower()
    query = RE_PUNCTUATION.sub(" ", query)
    # ‘ice-cream’ is coded in the news vectors as ‘ice_cream’
    query = query.replace("-", "_")
    query = query.strip()

    for word in query.split():
        if word in keys:
            ret.append(word)
        elif word.endswith("'s") and word[:-2] in keys:
            ret.append(word[:-2])
        elif "_" in word:
            # if ‘ice_cream’ not found, try ‘ice’ and ‘cream’
            for piece in word.split("_"):
                if piece in keys:
                    ret.append(piece)
                else:
                    _warn(piece, f"not found: {word!r} piece {piece!r}", already_warned)
        else:
            _warn(word, f"not found: {word!r}", already_warned)
    analysis = LABELS.linguistic_short.get_longest(
        tuple([t.strip("+") for t in analysis])
    )

    if analysis:
        ret.extend(extract_keyed_words(analysis, keys, already_warned))

    return uniq(ret)


def _warn(word, msg, already_warned):
    if (
        logger.isEnabledFor(logging.DEBUG)
        and already_warned is not None
        and word not in already_warned
    ):
        already_warned.add(word)
        logger.debug(msg)
