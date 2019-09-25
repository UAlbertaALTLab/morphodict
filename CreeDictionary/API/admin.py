from django.contrib import admin
from django.db.models import F, Q
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Definition, Inflection


class DefinitionInline(admin.TabularInline):
    model = Definition
    exclude = ("id",)
    extra = 0


class AlternativeSpellingFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("spelling")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "spelling_is"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("default", _("Default Spelling")),
            ("alternative", _("Alternative Spelling")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "default":
            return queryset.filter(Q(default_spelling__id=F("id")))

        if self.value() == "alternative":
            return queryset.filter(~Q(default_spelling__id=F("id")))


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

    list_display = (
        "text",
        "is_lemma",
        "has_paradigm",
        "is_default_spelling",
        "get_definitions",
        "get_keywords",
    )

    def has_paradigm(self, obj: Inflection):
        return not obj.as_is

    # noinspection Mypy,PyTypeHints
    has_paradigm.boolean = True  # type: ignore

    def is_default_spelling(self, obj: Inflection):
        return obj.default_spelling == obj

    # noinspection Mypy,PyTypeHints
    is_default_spelling.boolean = True  # type: ignore

    def get_keywords(self, obj: Inflection):
        if obj.is_lemma:
            lemma = obj
        else:
            lemma = obj.lemma

        keyword_texts = tuple(set([d.text for d in lemma.English.all()]))
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(keyword_texts)))
            % keyword_texts
        )

    # noinspection Mypy,PyTypeHints
    get_keywords.short_description = "ENGLISH KEYWORDS"  # type: ignore

    def get_definitions(self, obj: Inflection):
        if obj.is_lemma:
            lemma = obj
        else:
            lemma = obj.lemma

        definition_texts = [d.text for d in lemma.definition_set.all()]
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(definition_texts)))
            % tuple(definition_texts)
        )

    # noinspection Mypy,PyTypeHints
    get_definitions.short_description = "LEMMA DEFINITION"  # type: ignore
    list_filter = ("is_lemma", HasParadigmListFilter, AlternativeSpellingFilter)

    def get_lemma_form(self, obj: Inflection) -> str:
        return obj.lemma.text

    # noinspection Mypy,PyTypeHints
    get_lemma_form.short_description = "Lemma form"  # type: ignore

    def get_default_spelling(self, obj: Inflection) -> str:
        return obj.default_spelling.text

    # noinspection Mypy,PyTypeHints
    get_default_spelling.short_description = "Default spelling"  # type: ignore

    def get_lemma_definitions(self, obj: Inflection) -> str:
        definition_texts = [d.text for d in obj.lemma.definition_set.all()]
        return format_html(
            ("<br/><br/>".join(["<span>%s</span>"] * len(definition_texts)))
            % tuple(definition_texts)
        )

    # noinspection Mypy,PyTypeHints
    get_lemma_definitions.short_description = "Lemma definition"  # type: ignore

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.fields = ["text", "analysis", "is_lemma", "as_is"]
        self.readonly_fields = []

        inflection = Inflection.objects.get(pk=object_id)
        if inflection.is_lemma:
            self.inlines = [DefinitionInline]
        else:
            self.fields.append("get_lemma_form")
            self.fields.append("get_lemma_definitions")

            self.readonly_fields.append("get_lemma_form")
            self.readonly_fields.append("get_lemma_definitions")
            self.inlines = []

        if inflection.is_non_default_spelling():
            self.fields.append("get_default_spelling")
            self.readonly_fields.append("get_default_spelling")

        return super(InflectionAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    # todo: automatically increase id using transaction
    def add_view(self, request, form_url="", extra_context=None):

        self.exclude = ()
        return super(InflectionAdmin, self).add_view(request, form_url, extra_context)
