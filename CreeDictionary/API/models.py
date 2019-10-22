import unicodedata
from collections import defaultdict
from enum import Enum, auto
from typing import Optional, Set, List, Tuple, Dict
from urllib.parse import unquote
from pathlib import Path

from cree_sro_syllabics import syllabics2sro
from django.db import models, transaction
from django.db.models import QuerySet, Max

from constants import LC
from fuzzy_search import CreeFuzzySearcher
from shared import descriptive_analyzer_foma
from utils import fst_analysis_parser

import logging

# fixme: please give this class a better name
class Part(Enum):
    """
    corresponds to extra information we show to
    the user when user query matches an inflected form rather than a lemma
    like IC, Preverb, Reduplication, and Err/Orth
    """

    IC = "IC"  # initial change
    PRE = "PRE"  # preverbs


class Inflection(models.Model):
    _cree_fuzzy_searcher = None

    @classmethod
    def init_fuzzy_searcher(cls):
        if cls._cree_fuzzy_searcher is None:
            cls._cree_fuzzy_searcher = CreeFuzzySearcher(cls.objects.all())

    @classmethod
    def fuzzy_search(cls, query: str, distance: int) -> QuerySet:
        if cls._cree_fuzzy_searcher is None:
            return Inflection.objects.none()
        return cls._cree_fuzzy_searcher.search(query, distance)

    # override pk to allow use of bulk_create
    # auto-increment is also implemented in the overridden save below
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=40)

    RECOGNIZABLE_LC = [(lc.value,) * 2 for lc in LC] + [("", "")]
    lc = models.CharField(
        max_length=4,
        choices=RECOGNIZABLE_LC,
        help_text="lexical category parsed from xml",
    )
    RECOGNIZABLE_POS = [(p,) * 2 for p in ("IPV", "PRON", "N", "IPC", "V", "")]
    pos = models.CharField(
        max_length=4,
        choices=RECOGNIZABLE_POS,
        help_text="part of speech parsed from xml",
    )

    analysis = models.CharField(
        max_length=50,
        default="",
        help_text="fst analysis or the best possible if the source is not analyzable",
    )
    is_lemma = models.BooleanField(
        default=False, help_text="Lemma or non-lemma inflection"
    )
    as_is = models.BooleanField(
        default=False,
        help_text="Fst can not determine the lemma. Paradigm table will not be shown to the user for this entry",
    )

    default_spelling = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="alt_spellings"
    )

    lemma = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="inflections"
    )

    class Meta:
        # analysis is for faster user query (in function fetch_lemmas_by_user_query below)
        # text is for faster fuzzy search initialization when the app restarts on the server side (order_by text)
        indexes = [models.Index(fields=["analysis"]), models.Index(fields=["text"])]

    def __str__(self):
        return self.text

    def is_non_default_spelling(self) -> bool:
        return self.default_spelling != self

    def is_category(self, lc: LC) -> Optional[bool]:
        """
        :return: None if self.as_is is true. Meaning the analysis is simply the lc and the pos from the xml

        :raise ValueError: the lexical category of the lemma can not be recognized
        """
        if self.as_is:  # meaning the analysis is simply the lc and the pos from the xml
            return None
        category = hfstol_analysis_parser.extract_category(self.analysis)
        if category is None:
            raise ValueError(
                "The lexical category of the inflection %s can not be recognized. (A malformed analysis field?)"
                % self
            )
        return category is lc

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        ensures id is auto-incrementing. infer foreign key 'lemma' to be self if self.is_lemma is set to True.
         Default foreign key "default spelling" to self.
        """
        max_id = Inflection.objects.aggregate(Max("id"))
        if max_id["id__max"] is None:
            self.id = 0
        else:
            self.id = max_id["id__max"] + 1

        # infer foreign keys default spelling and lemma if they are not set.
        # this helps with adding entries in django admin as the ui for
        # foreign keys default spelling and lemma takes forever to
        # load.
        # Also helps with tests as it's now easier to create entries
        if self.default_spelling_id is None:
            self.default_spelling_id = self.id

        if self.is_lemma:
            self.lemma_id = self.id

        super(Inflection, self).save(*args, **kwargs)

    @staticmethod
    def fetch_lemma_by_user_query(
        user_query: str
    ) -> Tuple[Dict[str, List["Inflection"]], List["Inflection"]]:
        """
        treat the user query as cree and:

        Give the analysis of user query and matched lemmas.
        There can be multiple analysis for user queries
        One analysis could match multiple lemmas as well due to underspecified database fields.
        (lc and pos can be empty)

        treat the user query as English keyword and:

        Give a list of matched lemmas

        :param user_query: can be English or Cree (syllabics or not)
        :return: Dict with key being analysis for user query, values being lemmas. List of lemmas matched as if query is
         English word
        """

        # URL Decode
        user_query = unquote(user_query)
        # Whitespace won't affect results, but the FST can't deal with it:
        user_query = user_query.strip()
        # Normalize to UTF8 NFC
        user_query = unicodedata.normalize("NFC", user_query)
        user_query = (
            user_query.replace("ā", "â")
            .replace("ē", "ê")
            .replace("ī", "î")
            .replace("ō", "ô")
        )
        user_query = syllabics2sro(user_query)

        user_query = user_query.lower()

        # build up result_lemmas in 2 ways
        # 1. spell relax in descriptive fst
        # 2. definition containment of the query word
        lemmas_by_analysis: Dict[str, List["Inflection"]] = defaultdict(list)

        # utilize the spell relax in descriptive_analyzer
        # TODO: use shared.descriptive_analyzer (HFSTOL) when this bug is
        # fixed:
        # https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
        fst_analyses: Set[str] = set(
            "".join(a) for a in descriptive_analyzer_foma.analyze(user_query)
        )

        for analysis in fst_analyses:
            # todo: test
            if Inflection.objects.filter(analysis=analysis).first() is not None:
                # there can be multiple matches when there are different spellings
                # akocin|akocin+V+AI+Ind+Prs+3Sg
                # akociniw|akocin+V+AI+Ind+Prs+3Sg
                # In that case use the default_spelling field of either is ok,
                # both point correctly to the default spelling

                exact_match_lemma = (
                    Inflection.objects.filter(analysis=analysis)
                    .first()
                    .lemma.default_spelling
                )
                lemmas_by_analysis[analysis].append(exact_match_lemma)
            else:
                # When the user query is outside of paradigm tables
                # e.g. mad preverb and reduplication: ê-mâh-misi-nâh-nôcihikocik
                # e.g. Initial change: nêpât: {'IC+nipâw+V+AI+Cnj+Prs+3Sg'}
                # e.g. Err/Orth: ewapamat: {'PV/e+wâpamêw+V+TA+Cnj+Prs+3Sg+4Sg/PlO+Err/Orth'

                lemma_lc = fst_analysis_parser.extract_lemma_and_category(analysis)
                if lemma_lc is None:
                    logging.error(
                        f"fst_analysis_parser cannot understand analysis {analysis}"
                    )
                    continue

                lemma, lc = lemma_lc
                matched_lemmas = Inflection.objects.filter(text=lemma, is_lemma=True)

                # to eliminate alternative spellings
                met_lemma_analysis: Set[str] = set()
                for matched_lemma in matched_lemmas:
                    if (
                        matched_lemma.lc == "" or matched_lemma.lc == lc.value
                    ):  # underspecified or the same lc
                        if matched_lemma.analysis not in met_lemma_analysis:
                            lemmas_by_analysis[analysis].append(matched_lemma)
                        met_lemma_analysis.add(matched_lemma.analysis)

        # todo: remind user "are you searching in cree/english?"
        lemmas_by_english = []
        if " " not in user_query:  # a whole word
            lemma_ids = EnglishKeyword.objects.filter(text__iexact=user_query).values(
                "lemma__id"
            )
            lemmas_by_english = (
                Inflection.objects.filter(id__in=lemma_ids)
                .order_by("analysis")
                .distinct("analysis")
            )  # distinct analysis to remove alternative spellings
            # (note order_by is necessary for distinct to work by django docs)

        return lemmas_by_analysis, lemmas_by_english


class Definition(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=200)
    # space separated acronyms
    sources = models.CharField(max_length=5)

    lemma = models.ForeignKey(Inflection, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class EnglishKeyword(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=20)

    lemma = models.ForeignKey(
        Inflection, on_delete=models.CASCADE, related_name="English"
    )

    class Meta:
        indexes = [models.Index(fields=["text"])]
