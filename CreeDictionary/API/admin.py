from typing import Set

from cree_sro_syllabics import syllabics2sro
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from shared import descriptive_analyzer
from .models import Definition, DictionarySource, Wordform


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


# todo: make admin search "extended", searching for "nipa" should give result "nipâ"
# todo: show inflection definition when possible instead of always showing lemma definition
@admin.register(Wordform)
class InflectionAdmin(admin.ModelAdmin):
    search_fields = ("text",)

    def get_search_results(self, request, queryset, search_term):
        """

        :param request:
        :param queryset: queryset is search results
        :param search_term: what you input in admin site
        :return:
        """

        queryset, use_distinct = super(InflectionAdmin, self).get_search_results(
            request, queryset, search_term
        )
        if not search_term:
            return queryset, use_distinct

        search_term = (
            search_term.replace("ā", "â")
            .replace("ē", "ê")
            .replace("ī", "î")
            .replace("ō", "ô")
        )
        search_term = syllabics2sro(search_term)

        search_term = search_term.lower()

        # utilize the spell relax in descriptive_analyzer
        fst_analyses: Set[str] = descriptive_analyzer.feed_in_bulk_fast([search_term])[
            search_term
        ]
        unfiltered_queryset = Wordform.objects.filter(analysis__in=fst_analyses)
        unfiltered_queryset |= Wordform.objects.filter(text=search_term)
        return unfiltered_queryset & queryset, True

    list_display = (
        "text",
        "is_lemma",
        "has_paradigm",
        "get_definitions",
        "get_keywords",
        "id",
    )

    def has_paradigm(self, obj: Wordform):
        return not obj.as_is

    # noinspection Mypy,PyTypeHints
    has_paradigm.boolean = True  # type: ignore

    def get_keywords(self, obj: Wordform):
        if obj.is_lemma:
            lemma = obj
        else:
            lemma = obj.lemma

        keyword_texts = tuple(set([d.text for d in lemma.english_keyword.all()]))
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(keyword_texts)))
            % keyword_texts
        )

    # noinspection Mypy,PyTypeHints
    get_keywords.short_description = "ENGLISH KEYWORDS"  # type: ignore

    def get_definitions(self, obj: Wordform):
        if obj.is_lemma:
            lemma = obj
        else:
            lemma = obj.lemma

        definition_texts = [d.text for d in lemma.definitions.all()]
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(definition_texts)))
            % tuple(definition_texts)
        )

    # noinspection Mypy,PyTypeHints
    get_definitions.short_description = "LEMMA DEFINITION"  # type: ignore
    list_filter = ("is_lemma", HasParadigmListFilter)

    def get_lemma_form(self, obj: Wordform) -> str:
        return obj.lemma.text

    # noinspection Mypy,PyTypeHints
    get_lemma_form.short_description = "Lemma form"  # type: ignore

    def get_lemma_definitions(self, obj: Wordform) -> str:
        definition_texts = [d.text for d in obj.lemma.definitions.all()]
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(definition_texts)))
            % tuple(definition_texts)
        )

    # noinspection Mypy,PyTypeHints
    get_lemma_definitions.short_description = "Lemma definition"  # type: ignore

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.fields = ["text", "analysis", "is_lemma", "as_is", "pos", "full_lc", "id"]
        self.readonly_fields = ["id"]

        inflection = Wordform.objects.get(pk=object_id)
        if inflection.is_lemma:
            self.inlines = [DefinitionInline]
        else:
            self.fields.append("get_lemma_form")
            self.fields.append("get_lemma_definitions")

            self.readonly_fields.append("get_lemma_form")
            self.readonly_fields.append("get_lemma_definitions")
            self.inlines = []

        return super(InflectionAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        # id is auto incremented upon save
        # lemma takes too long to load
        # if is_lemma is set to true, lemma will be set to self
        self.exclude = ("id", "lemma")

        return super(InflectionAdmin, self).add_view(request, form_url, extra_context)


@admin.register(DictionarySource)
class DictionarySourceAdmin(admin.ModelAdmin):
    """
    Allows you to edit the bibliographic details of a dictionary source.
    """
