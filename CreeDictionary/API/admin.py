from django.contrib import admin
from .models import *


class InflectionInline(admin.TabularInline):
    model = Inflection


#
class DefinitionInline(admin.TabularInline):
    model = Definition
    exclude = ("id",)
    extra = 0


@admin.register(Inflection)
class InflectionAdmin(admin.ModelAdmin):
    search_fields = ("text",)

    list_display = ("text", "is_lemma", "as_is")
    list_filter = ("is_lemma", "as_is")
    exclude = ("id",)
    inlines = [DefinitionInline]
    # list_display = ("text",)


# admin.site.register(Definition, InflectionAdmin)
# admin.site.register(Inflection, InflectionAdmin)
