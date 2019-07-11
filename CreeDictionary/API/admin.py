from django.contrib import admin
from .models import *


class AttributeInline(admin.TabularInline):
    model = Attribute


class InflectionInline(admin.TabularInline):
    model = Inflection


class InfelctionFormInline(admin.TabularInline):
    model = InflectionForm


class DefinitionInline(admin.TabularInline):
    model = Definition


class LemmaAdmin(admin.ModelAdmin):
    inlines = [InflectionInline, AttributeInline, ]


class InflectionAdmin(admin.ModelAdmin):
    inlines = [InfelctionFormInline, ]


class WordAdmin(admin.ModelAdmin):
    inlines = [DefinitionInline, ]
