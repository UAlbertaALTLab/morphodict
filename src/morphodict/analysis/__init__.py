import logging
from functools import cache

from hfst_optimized_lookup import TransducerFile, Analysis
from django.conf import settings

FST_DIR = settings.BASE_DIR / "resources" / "fst"


@cache
def strict_generator():
    return TransducerFile(FST_DIR / settings.STRICT_GENERATOR_FST_FILENAME)


@cache
def relaxed_analyzer():
    return TransducerFile(FST_DIR / settings.RELAXED_ANALYZER_FST_FILENAME)


@cache
def strict_analyzer():
    return TransducerFile(FST_DIR / settings.STRICT_ANALYZER_FST_FILENAME)


def rich_analyze_relaxed(text):
    return list(
        RichAnalysis(r) for r in relaxed_analyzer().lookup_lemma_with_affixes(text)
    )


def rich_analyze_strict(text):
    return list(
        RichAnalysis(r) for r in strict_analyzer().lookup_lemma_with_affixes(text)
    )


class RichAnalysis:
    """The one true FST analysis class.

    Put all your methods for dealing with things like `PV/e+nipâw+V+AI+Cnj+3Pl`
    here.
    """

    def __init__(self, analysis):
        if isinstance(analysis, Analysis):
            self._tuple = analysis
        elif (isinstance(analysis, list) or isinstance(analysis, tuple)) and len(
            analysis
        ) == 3:
            prefix_tags, lemma, suffix_tags = analysis
            self._tuple = Analysis(
                prefixes=tuple(prefix_tags), lemma=lemma, suffixes=tuple(suffix_tags)
            )
        else:
            raise Exception(f"Unsupported argument: {analysis=!r}")

    @property
    def tuple(self):
        return self._tuple

    @property
    def lemma(self):
        return self._tuple.lemma

    @property
    def prefix_tags(self):
        return self._tuple.prefixes

    @property
    def suffix_tags(self):
        return self._tuple.suffixes

    def generate(self):
        return strict_generator().lookup(self.smushed())

    def smushed(self):
        return "".join(self.prefix_tags) + self.lemma + "".join(self.suffix_tags)

    def tag_set(self):
        return set(self.suffix_tags + self.prefix_tags)

    def tag_intersection_count(self, other):
        """How many tags does this analysis have in common with another?"""
        if not isinstance(other, RichAnalysis):
            raise Exception(f"Unsupported argument: {other=!r}")
        return len(self.tag_set().intersection(other.tag_set()))

    def __iter__(self):
        """Allows doing `head, _, tail = rich_analysis`"""
        return iter(self._tuple)

    def __hash__(self):
        return hash(self._tuple)

    def __eq__(self, other):
        if not isinstance(other, RichAnalysis):
            return NotImplemented
        return self._tuple == other.tuple

    def __repr__(self):
        return f"RichAnalysis({[self.prefix_tags, self.lemma, self.suffix_tags]!r})"
