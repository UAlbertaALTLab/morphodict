import re
from functools import cache

from django.conf import settings
from hfst import is_diacritic # type: ignore
from hfst_altlab import TransducerFile
from hfst_altlab.types import Analysis, FullAnalysis, Wordform

FST_DIR = settings.BASE_DIR / "resources" / "fst"


@cache
def strict_generator():
    return TransducerFile(FST_DIR / settings.STRICT_GENERATOR_FST_FILENAME)


@cache
def strict_generator_with_morpheme_boundaries():
    try:
        return TransducerFile(
            FST_DIR / settings.STRICT_GENERATOR_WITH_BOUNDARIES_FST_FILENAME
        )
    except IsADirectoryError:
        return strict_generator()
    except FileNotFoundError:
        return strict_generator()


@cache
def relaxed_analyzer():
    return TransducerFile(FST_DIR / settings.RELAXED_ANALYZER_FST_FILENAME)


@cache
def strict_analyzer():
    return TransducerFile(FST_DIR / settings.STRICT_ANALYZER_FST_FILENAME)

def filter_derivational_analyses(analyses: list[FullAnalysis]):
    """
    This method currently hard-codes the strategy discussed with Antti of
    - First provide only the analyses that have no derivational component
    - If only analyses with "+Der/..." tags, provide all those analyses with
      those tags **except** for the "+Der/N" and "+Der/V" tags.
    - If previous list is empty, provide the analysis left (which would be only
      "+Der/N" and "+Der/V" analyses)
    """
    annotated_analyses: list[tuple[list[str], FullAnalysis]] = [
        ([ t[4:] for t in analysis.tokens if t.startswith("+Der/") or (t.startswith("PV/") and t not in ["PV/ê+", "PV/kâ+", "PV/kî+", "PV/wî+", "PV/ka+"])], analysis) 
        for analysis in analyses ]
    current_level = [ analysis for (derivational_tokens, analysis) in annotated_analyses if not derivational_tokens]
    if current_level:
        return current_level
    current_level = [ analysis for (derivational_tokens, analysis) in annotated_analyses if derivational_tokens and not any(token in ["N", "V"] for token in derivational_tokens)]
    if current_level:
        return current_level
    return [ analysis for (derivational_tokens, analysis) in annotated_analyses if derivational_tokens and any(token in ["N", "V"] for token in derivational_tokens)]

def reify_preverb_tags_in_fullanalysis(analysis: FullAnalysis) -> Analysis:
    """
    TODO: This method is required for new derivational FSTs that DO NOT follow 
    the previous "multichar-prefixes singlechar-lemma multichar-suffixes"
    convention for the output stream of non-flag diacritic tokens coming from
    the FST.  We need to likely encode this as a pass on the FSTs to restore the
    invariant so that altlab-hfst tools are available and usable to other users
    of the FST that expect the convention to hold or ditch the convention
    altogether and provide a more ad-hoc way in libraries to reconstruct an
    analysis from the output stream of non-diacritic tokens.
    """
    prefix_tags: list[str] = []
    lemma_chars: list[str] = []
    suffix_tags: list[str] = []

    tag_destination = prefix_tags
    is_a_preverb = False
    preverb_tag_start = "PV/"
    current_preverb = preverb_tag_start
    preverb_tag_end = "+"

    for symbol in analysis.tokens:
        if not is_diacritic(symbol):
            if len(symbol) == 1 and not is_a_preverb:
                lemma_chars.append(symbol)
                tag_destination = suffix_tags
            elif is_a_preverb:
                if symbol == preverb_tag_end:
                    tag_destination.append(current_preverb+preverb_tag_end)
                    current_preverb = preverb_tag_start
                    is_a_preverb = False
                else:
                    current_preverb += symbol
            elif symbol == preverb_tag_start:
                is_a_preverb = True
            else:
                tag_destination.append(symbol)

    return Analysis(
        tuple(prefix_tags),
        "".join(lemma_chars),
        tuple(suffix_tags),
    )


class RichAnalysis:
    """The one true FST analysis class.

    Put all your methods for dealing with things like `PV/ê+nipâw+V+AI+Cnj+3Pl`
    here.
    """

    _tuple: Analysis
    weight: float

    def __init__(self, analysis: FullAnalysis | tuple):
        if isinstance(analysis, FullAnalysis):
            self._tuple = reify_preverb_tags_in_fullanalysis(analysis)
            self.weight = analysis.weight
        elif (isinstance(analysis, list) or isinstance(analysis, tuple)) and len(
            analysis
        ) in [3, 4]:
            if len(analysis) == 3:
                prefix_tags, lemma, suffix_tags = analysis
                weight = 0.0
            else:
                prefix_tags, lemma, suffix_tags, weight = analysis
            self._tuple = Analysis(
                prefixes=tuple(prefix_tags), lemma=lemma, suffixes=tuple(suffix_tags)
            )
            self.weight = weight
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

    def generate(self) -> list[str]:
        # TODO: Split in generation by precategorized tokens
        return [
            r.wordform
            for r in strict_generator().weighted_lookup_full_wordform(self.smushed())
        ]

    def generate_with_morphemes(self, inflection: str) -> list[str] | None:
        # TODO
        try:
            results: list[
                Wordform
            ] = strict_generator_with_morpheme_boundaries().weighted_lookup_full_wordform(
                self.smushed()
            )
            if len(results) != 1:
                for result in results:
                    if "".join(re.split(r"[<>]", result.wordform)) == inflection:
                        return re.split(r"[<>]", result.wordform)
                return None
            return re.split(r"[<>]", results[0].wordform)
        except RuntimeError as e:
            print("Could not generate morphemes:", e)
            return []

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

def rich_analyze_relaxed(text: str) -> list[RichAnalysis]:
    return list(
        RichAnalysis(r) for r in filter_derivational_analyses(relaxed_analyzer().weighted_lookup_full_analysis(text))
    )

def rich_analyze_strict(text: str) -> list[RichAnalysis]:
    return list(
        RichAnalysis(r) for r in filter_derivational_analyses(strict_analyzer().weighted_lookup_full_analysis(text))
    )
