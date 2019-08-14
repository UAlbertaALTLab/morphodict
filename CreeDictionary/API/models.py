from django.db import models


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


class Definition(models.Model):
    # override pk to allow use of bulk_create
    id = models.PositiveIntegerField(primary_key=True)

    text = models.CharField(max_length=200)
    # space separated acronyms
    sources = models.CharField(max_length=5)

    lemma = models.ForeignKey(Inflection, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
