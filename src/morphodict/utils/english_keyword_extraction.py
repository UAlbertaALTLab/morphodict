import re
from typing import Set

import snowballstemmer

word_pattern = re.compile(r"[\w.\-/']+")

stop_words = {"a", "an", "the", "s/he", "s.o.", "s.t.", "it/him"}

stemmer = snowballstemmer.EnglishStemmer()


def stem_keywords(translation: str) -> Set[str]:
    """
    returns lowercased keywords from the translation, by stripping stop words like a/an s/he s.o. s.t.

    >>> sorted(stem_keywords("s/he is of a that kind (previously mentioned)"))
    ['is', 'kind', 'mention', 'of', 'previous', 'that']
    """
    words = set(word_pattern.findall(translation.lower()))

    # .strip('.') is because of the trailing periods in some translation
    return set(
        stemmer.stemWords([word.strip(".") for word in words if word not in stop_words])
    )
