from typing import NamedTuple, Tuple


class Analysis(NamedTuple):
    """
    An analysis of a wordform.

    This is a *named tuple*, so you can use it both with attributes and indices:

    >>> analysis = Analysis(('PV/e+',), 'wâpamêw', ('+V', '+TA', '+Cnj', '+3Sg', '+4Sg/PlO'))

    Using attributes:

    >>> analysis.lemma
    'wâpamêw'
    >>> analysis.prefixes
    ('PV/e+',)
    >>> analysis.suffixes
    ('+V', '+TA', '+Cnj', '+3Sg', '+4Sg/PlO')

    Using with indices:

    >>> len(analysis)
    3
    >>> analysis[0]
    ('PV/e+',)
    >>> analysis[1]
    'wâpamêw'
    >>> analysis[2]
    ('+V', '+TA', '+Cnj', '+3Sg', '+4Sg/PlO')
    >>> prefixes, lemma, suffix = analysis
    >>> lemma
    'wâpamêw'
    """

    prefixes: Tuple[str, ...]
    """
    Tags that appear before the lemma.
    """

    lemma: str
    """
    The base form of the analyzed wordform.
    """

    suffixes: Tuple[str, ...]
    """
    Tags that appear after the lemma.
    """
