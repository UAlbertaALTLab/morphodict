import unicodedata
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from django.db import models

# todo: override save() to automatically increase id
# see: https://docs.djangoproject.com/en/2.2/topics/db/models/#overriding-predefined-model-methods
from constants import LexicalCategory
from shared import descriptive_analyzer
from utils import hfstol_analysis_parser


class Inflection(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=40)
    analysis = models.CharField(max_length=50, default="")
    is_lemma = models.BooleanField(
        default=False, help_text="Lemma or non-lemma inflection"
    )
    as_is = models.BooleanField(
        default=False,
        help_text="Fst can not determine the lemma. Paradigm table will not be shown to the user for this entry",
    )

    class Meta:
        indexes = [models.Index(fields=["text"])]

    def __str__(self):
        return self.text

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
    def fetch_lemmas_by_fst_analysis(cls, analysis: str) -> List["Inflection"]:
        """
        :return: can be empty
        """
        lemma_category = hfstol_analysis_parser.extract_lemma_and_category(analysis)
        if lemma_category is None:
            return []
        lemma, category = lemma_category

        matched_lemmas: List[Inflection] = []
        for db_lemma in cls.objects.filter(text=lemma, is_lemma=True):
            if db_lemma.is_category(lemma_category):
                matched_lemmas.append(db_lemma)

        return matched_lemmas


class Definition(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=200)
    # space separated acronyms
    sources = models.CharField(max_length=5)

    lemma = models.ForeignKey(Inflection, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
