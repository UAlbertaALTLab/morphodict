import re
from typing import List

import snowballstemmer

word_pattern = re.compile(r"[\w.\-/']+")

stop_words = {"a", "an", "the", "s/he", "s.o.", "s.t."}

stemmer = snowballstemmer.EnglishStemmer()


def extract_keywords(translation: str) -> List[str]:
    """
    returns lowercased keywords from the translation, by stripping stop words like a/an s/he s.o. s.t.

    returned list has no duplicates

    >>> sorted(extract_keywords("s/he is of a that kind (previously mentioned)"))
    ['is', 'kind', 'mention', 'of', 'previous', 'that']
    """
    words = set(word_pattern.findall(translation.lower()))

    # .strip('.') is because of the trailing periods in some translation
    return stemmer.stemWords(
        {word.strip(".") for word in words if word not in stop_words}
    )
