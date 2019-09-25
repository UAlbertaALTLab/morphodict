import time
import unicodedata
from typing import List, Optional, Set, Dict
from urllib.parse import unquote

from cree_sro_syllabics import syllabics2sro
from django.db import models, connection

# todo: override save() to automatically increase id (so that people can add words on django admin)
# see: https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods
from django.db.models import QuerySet
from django.forms import model_to_dict

from constants import LexicalCategory
from fuzzy_search import CreeFuzzySearcher
from shared import descriptive_analyzer
from utils import hfstol_analysis_parser


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
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=40)

    RECOGNIZABLE_LC = [(lc.value,) * 2 for lc in LexicalCategory] + [("", "")]
    lc = models.CharField(max_length=4, choices=RECOGNIZABLE_LC)
    RECOGNIZABLE_POS = ((p,) * 2 for p in ("IPV", "PRON", "N", "IPC", "V", ""))
    pos = models.CharField(max_length=4, choices=RECOGNIZABLE_POS)

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

    def is_category(self, lc: LexicalCategory) -> Optional[bool]:
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

    @classmethod
    def fetch_non_as_is_lemmas_by_fst_analysis(
        cls, analysis: str
    ) -> List["Inflection"]:
        """
        :return: can be empty
        """
        lemma_category = hfstol_analysis_parser.extract_lemma_and_category(analysis)
        if lemma_category is None:
            return []
        lemma, category = lemma_category

        matched_lemmas: List[Inflection] = []
        for db_lemma in cls.objects.filter(text=lemma, is_lemma=True, as_is=False):
            if db_lemma.is_category(category):
                matched_lemmas.append(db_lemma)

        return matched_lemmas

    @classmethod
    def fetch_lemmas_by_user_query(cls, user_query: str) -> QuerySet:
        """

        :param user_query: can be English or Cree (syllabics or not)
        :return: can be empty
        """
        # todo: tests
        # fixme: paradigm for niska vanishes the second time you click

        # URL Decode
        user_query = unquote(user_query)
        # Normalize to UTF8 NFC
        user_query = unicodedata.normalize("NFC", user_query)
        user_query = (
            user_query.replace("ā", "â")
            .replace("ē", "ê")
            .replace("ī", "î")
            .replace("ō", "ô")
        )
        user_query = syllabics2sro(user_query)

        # todo (for matt): there are capped words in xml.
        # make fuzzy search treat capital letters the same as lower case letters
        user_query = user_query.lower()

        # build up result_lemmas in 3 ways
        # 1. spell relax in descriptive fst
        # 2. fuzzy search
        #
        # 3. definition containment of the query word
        result_lemmas = Inflection.objects.none()

        # utilize the spell relax in descriptive_analyzer
        fst_analyses: Set[str] = descriptive_analyzer.feed_in_bulk_fast([user_query])[
            user_query
        ]
        lemma_ids = Inflection.objects.filter(analysis__in=fst_analyses).values(
            "lemma__id"
        )

        result_lemmas |= Inflection.objects.filter(id__in=lemma_ids)
        if len(user_query) > 1:
            # fuzzy search does not make sense for a single letter, it will just give every single letter word
            lemma_ids = Inflection.fuzzy_search(user_query, 1).values("lemma__id")
        result_lemmas |= Inflection.objects.filter(id__in=lemma_ids)

        # todo: remind user "are you searching in cree/english?"
        if " " not in user_query:  # a whole word

            lemma_ids = EnglishKeyword.objects.filter(text__iexact=user_query).values(
                "lemma__id"
            )
            result_lemmas |= Inflection.objects.filter(id__in=lemma_ids)

        return result_lemmas


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
