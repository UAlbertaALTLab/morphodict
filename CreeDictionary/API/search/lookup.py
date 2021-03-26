import logging
from typing import Iterable, Set

from django.db.models import Q

from API.models import (
    Wordform,
    EnglishKeyword,
)
from CreeDictionary import hfstol
from utils import get_modified_distance, fst_analysis_parser, PartOfSpeech
from utils.english_keyword_extraction import stem_keywords
from utils.types import ConcatAnalysis
from .affix import (
    do_cree_affix_seach,
    do_english_affix_search,
    query_would_return_too_many_results,
)
from .core import _BaseWordformSearch, fetch_preverbs
from .types import (
    CreeAndEnglish,
    InternalForm,
    CreeResult,
    EnglishResult,
    Lemma,
    MatchedEnglish,
)

logger = logging.getLogger(__name__)


class WordformSearchWithExactMatch(_BaseWordformSearch):
    """
    Searches for exact matches in both the wordforms and EnglishKeyword tables.
    """

    def fetch_bilingual_results(self) -> CreeAndEnglish:
        return fetch_cree_and_english_results(self.cleaned_query, affix_search=False)


class WordformSearchWithAffixes(_BaseWordformSearch):
    """
    Same as WordformSearchWithExactMatch, but augments results with searches on affixes.
    """

    def fetch_bilingual_results(self) -> CreeAndEnglish:
        return fetch_cree_and_english_results(self.cleaned_query, affix_search=True)


def filter_cw_wordforms(q: Iterable[Wordform]) -> Iterable[Wordform]:
    """
    return the wordforms that has definition from CW dictionary

    :param q: an Iterable of Wordforms
    """
    for wordform in q:
        for definition in wordform.definitions.all():
            if "CW" in definition.source_ids:
                yield wordform
                break


def fetch_cree_and_english_results(
    user_query: InternalForm, affix_search: bool = True
) -> CreeAndEnglish:
    """
    HERE BE DRAGONS!

    Historically, this function has been the bulk of our search backend, performing both
    Cree and English search. However, I honestly don't understand how it works. As of
    this writing (2021-01-11), I am refactoring the function to bring some order to it
    and hopefully understanding how it works.

    Original documentation for fetch_lemma_by_user_query() as follows (I don't really understand it):

    ---

    treat the user query as cree and:

    Give the analysis of user query and matched lemmas.
    There can be multiple analysis for user queries
    One analysis could match multiple lemmas as well due to underspecified database fields.
    (inflectional_category and pos can be empty)

    treat the user query as English keyword and:

    Give a list of matched lemmas

    :param affix_search: whether to perform affix search or not (both English and Cree)
    :param user_query: can be English or Cree (syllabics or not)
    """

    # build up result_lemmas in 2 ways
    # 1. affix search (return all results that ends/starts with the query string)
    # 2. spell relax in descriptive fst
    # 2. definition containment of the query word

    cree_results: Set[CreeResult] = set()
    english_results: Set[EnglishResult] = set()

    # there will be too many matches for some shorter queries
    if affix_search and not query_would_return_too_many_results(user_query):
        do_cree_affix_seach(user_query, cree_results)
        do_english_affix_search(user_query, english_results)

    _fetch_results(user_query, cree_results, english_results)

    return CreeAndEnglish(cree_results, english_results)


def _fetch_results(
    user_query: InternalForm,
    cree_results: Set[CreeResult],
    english_results: Set[EnglishResult],
):
    """
    The rest of this method is code Eddie has NOT refactored, so I don't really
    understand what's going on here:
    """
    # Use the spelling relaxation to try to decipher the query
    #   e.g., "atchakosuk" becomes "acâhkos+N+A+Pl" --
    #         thus, we can match "acâhkos" in the dictionary!
    fst_analyses: Set[ConcatAnalysis] = set(
        a.concatenate() for a in hfstol.analyze(user_query)
    )

    all_standard_forms = []

    for analysis in fst_analyses:
        # todo: test

        exactly_matched_wordforms = Wordform.objects.filter(
            analysis=analysis, as_is=False
        )

        if exactly_matched_wordforms.exists():
            for wf in exactly_matched_wordforms:
                cree_results.add(
                    CreeResult(ConcatAnalysis(wf.analysis), wf, Lemma(wf.lemma))
                )
        else:
            # When the user query is outside of paradigm tables
            # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
            # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+3Sg'}

            lemma_wc = fst_analysis_parser.extract_lemma_text_and_word_class(analysis)
            if lemma_wc is None:
                logger.error(
                    f"fst_analysis_parser cannot understand analysis {analysis}"
                )
                continue

            # now we generate the standardized form of the user query for display purpose
            normatized_form_for_analysis = list(hfstol.generate(analysis))
            all_standard_forms.extend(normatized_form_for_analysis)
            if len(all_standard_forms) == 0:
                logger.error(
                    f"can not generate standardized form for analysis {analysis}"
                )
            normatized_user_query = min(
                normatized_form_for_analysis,
                key=lambda f: get_modified_distance(f, user_query),
            )

            lemma, word_class = lemma_wc
            matched_lemma_wordforms = Wordform.objects.filter(text=lemma, is_lemma=True)

            # now we get wordform objects from database
            # Note:
            # non-analyzable matches should not be displayed (mostly from MD)
            # like "nipa", which means kill him
            # those results are filtered out by `as_is=False` below
            # suggested by Arok Wolvengrey

            if word_class.pos is PartOfSpeech.PRON:
                # specially handle pronouns.
                # this is a temporary fix, otherwise "ôma" won't appear in the search results, since
                # "ôma" has multiple analysis
                # ôma+Ipc+Foc
                # ôma+Pron+Dem+Prox+I+Sg
                # ôma+Pron+Def+Prox+I+Sg
                # it's ambiguous which one is the lemma in the importing process thus it's labeled "as_is"

                # a more permanent fix requires every pronouns lemma to be listed and specified
                for lemma_wordform in matched_lemma_wordforms:
                    cree_results.add(
                        CreeResult(
                            ConcatAnalysis(analysis),
                            normatized_user_query,
                            Lemma(lemma_wordform),
                        )
                    )
            else:
                for lemma_wordform in matched_lemma_wordforms.filter(
                    as_is=False, pos=word_class.pos.name
                ):
                    cree_results.add(
                        CreeResult(
                            ConcatAnalysis(analysis),
                            normatized_user_query,
                            Lemma(lemma_wordform),
                        )
                    )

    # we choose to trust CW and show those matches with definition from CW.
    # text__in = all_standard_forms help match those lemmas that are labeled as_is but trust-worthy nonetheless
    # because they come from CW
    # text__in = [user_query] help matching entries with spaces in it, which fst can't analyze.
    for cw_as_is_wordform in filter_cw_wordforms(
        Wordform.objects.filter(
            text__in=all_standard_forms + [user_query],
            as_is=True,
            is_lemma=True,
        )
    ):
        cree_results.add(
            CreeResult(
                ConcatAnalysis(cw_as_is_wordform.analysis),
                cw_as_is_wordform,
                Lemma(cw_as_is_wordform),
            )
        )

    # as per https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/161
    # preverbs should be presented
    # exhaustively search preverbs here (since we can't use fst on preverbs.)

    for preverb_wf in fetch_preverbs(user_query):
        cree_results.add(
            CreeResult(
                ConcatAnalysis(preverb_wf.analysis),
                preverb_wf,
                Lemma(preverb_wf),
            )
        )

    # Words/phrases with spaces in CW dictionary can not be analyzed by fst and are labeled "as_is".
    # However we do want to show them. We trust CW dictionary here and filter those lemmas that has any definition
    # that comes from CW

    # now we get results searched by English
    # todo: remind user "are you searching in cree/english?"
    # todo: allow inflected forms to be searched through English. (requires database migration
    #  since now EnglishKeywords are bound to lemmas)
    for stemmed_keyword in stem_keywords(user_query):

        lemma_ids = EnglishKeyword.objects.filter(text__iexact=stemmed_keyword).values(
            "lemma__id"
        )

        for wordform in Wordform.objects.filter(id__in=lemma_ids):
            english_results.add(
                EnglishResult(MatchedEnglish(user_query), wordform, Lemma(wordform))
            )  # will become  (user_query, inflection.text, inflection.lemma)

        # explained above, preverbs should be presented
        for wordform in Wordform.objects.filter(
            Q(pos="IPV") | Q(inflectional_category="IPV") | Q(pos="PRON"),
            id__in=lemma_ids,
            as_is=True,
        ):
            english_results.add(
                EnglishResult(MatchedEnglish(user_query), wordform, Lemma(wordform))
            )  # will become  (user_query, inflection.text, wordform)

    return CreeAndEnglish(cree_results, english_results)
