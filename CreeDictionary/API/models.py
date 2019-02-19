from django.db import models

class Definition(models.Model):
    context = models.CharField(max_length=200)
    source = models.CharField(max_length=8)

class Word(models.Model):
    context = models.CharField(max_length=50)
    definitions = models.ForeignKey(Definition)

class InflectionForm(models.Model):
    name = models.CharField(max_length=10)

class Inflection(Word):
    inflectionForms = models.ForeignKey(InflectionForm)

class Attribute(models.Model):
    name = models.CharField(max_length=10)

class Lemma(Word):
    inflections = models.ForeignKey(Inflection)
    attributes = models.ForeignKey(Attribute)