import unicodedata
from typing import List, Optional, Set, Tuple, Iterable
from urllib.parse import unquote

from cree_sro_syllabics import syllabics2sro
from django.db import models

# todo: override save() to automatically increase id
# see: https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods
from constants import LexicalCategory, LC
from shared import descriptive_analyzer
from utils import hfstol_analysis_parser


class Inflection(models.Model):
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
        indexes = [models.Index(fields=["text"])]

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

    def find_lemma(self) -> List["Inflection"]:
        """
        should be implemented in the Inflection class
        """
        # todo: factor out Lemma class and Inflection class.
        # each
        pass

    @classmethod
    def fetch_by_user_query(cls, user_query: str) -> List["Inflection"]:
        """

        :param user_query: can be English or Cree (syllabics or not)
        :return: can be empty
        """
        # todo: tests?

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

        # todo: there are capped words in xml.
        # 1. make fuzzy search treat capital letters the same as lower case letters
        # 2. make data-fetching classmethods in Inflection model class treat capital letters the same as lower case letters
        user_query = user_query.lower()

        fst_analyses: Set[str] = descriptive_analyzer.feed_in_bulk_fast([user_query])[
            user_query
        ]
        lemma_and_categories = [
            hfstol_analysis_parser.extract_lemma_and_category(a) for a in fst_analyses
        ]
        recognized_lemma_and_categories: List[Tuple[str, LC]] = list(
            filter(lambda x: x is not None, lemma_and_categories)
        )
        recognized_lemmas = [l_lc[0] for l_lc in recognized_lemma_and_categories]

        fetched_lemmas = []

        if len(user_query) > 2:
            from fuzzy_search import CreeFuzzySearcher

            fuzzy_inflections: Iterable[Inflection] = CreeFuzzySearcher().search(
                user_query, 1
            )

        if len(recognized_lemmas) > 0:
            # Probably Cree
            fetched_lemmas.extend(
                list(
                    Inflection.objects.filter(is_lemma=True, text__in=recognized_lemmas)
                )
            )
        else:
            # Probably English
            fetched_lemmas.extend(
                list(
                    Inflection.objects.filter(
                        is_lemma=True, definition__text__icontains=user_query
                    )
                )
            )

        return fetched_lemmas


class Definition(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=200)
    # space separated acronyms
    sources = models.CharField(max_length=5)

    lemma = models.ForeignKey(Inflection, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
