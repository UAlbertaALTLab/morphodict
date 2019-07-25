from django.contrib import admin
from .models import *





class InflectionInline(admin.TabularInline):
    model = Inflection

#
# class InfelctionFormInline(admin.TabularInline):
#     model = InflectionForm


class DefinitionInline(admin.TabularInline):
    model = Definition





class InflectionAdmin(admin.ModelAdmin):
    pass




admin.site.register(Source)
admin.site.register(Inflection)
