from typing import Set
import re

word_pattern = re.compile(r"[\w.\-/']+")

stop_words = {"a", "an", "the", "s/he", "s.o.", "s.t."}


def extract_keywords(translation: str) -> Set[str]:
    """
    returns lowercased keywords from the translation, by stripping stop words like a/an s/he s.o. s.t.

    >>> extract_keywords("s/he is of a that kind (previously mentioned)") == {'is', 'of', 'that', 'kind', 'previously', 'mentioned'}
    True
    """
    words = set(word_pattern.findall(translation.lower()))

    # .strip('.') is because of the trailing periods in some translation
    return {word.strip(".") for word in words if word not in stop_words}
