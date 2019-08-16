from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import *


# @admin.register(Definition)
# class DefinitionAdmin(admin.ModelAdmin):
#     model = Definition


class DefinitionInline(admin.TabularInline):
    model = Definition
    exclude = ("id",)
    extra = 0


class HasParadigmListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("paradigm")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "has_paradigm"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ("true", _("Has paradigm")), ("false", _("Does not have paradigm"))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "true":
            return queryset.filter(as_is=False)

        if self.value() == "false":
            return queryset.filter(as_is=True)


@admin.register(Inflection)
class InflectionAdmin(admin.ModelAdmin):
    # todo: use fuzzy search and spell relax in the admin
    search_fields = ("text",)

    list_display = ("text", "is_lemma", "has_paradigm", "get_definitions")

    def has_paradigm(self, obj: Inflection):
        return not obj.as_is

    has_paradigm.boolean = True

    def get_definitions(self, obj: Inflection):
        definition_texts = [d.text for d in obj.definition_set.all()]
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(definition_texts)))
            % tuple(definition_texts)
        )

    get_definitions.short_description = "DEFINITION"
    list_filter = ("is_lemma", HasParadigmListFilter)

    # list_display = ("text",)
    exclude = ("id",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if Inflection.objects.get(pk=object_id).is_lemma:
            self.inlines = [DefinitionInline]
        else:
            self.inlines = []

        return super(InflectionAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    # todo: automatically increase id using transaction
    def add_view(self, request, form_url="", extra_context=None):

        self.exclude = ()
        return super(InflectionAdmin, self).add_view(request, form_url, extra_context)
