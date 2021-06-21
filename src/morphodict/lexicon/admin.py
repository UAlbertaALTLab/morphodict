from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from morphodict.lexicon.models import (
    Definition,
    DictionarySource,
    TargetLanguageKeyword,
    Wordform,
    SourceLanguageKeyword,
)


# https://stackoverflow.com/a/1720961/14558
def admin_url_for(obj):
    return reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=[obj.id],
    )


class CustomModelAdmin(admin.ModelAdmin):
    # Make everything read-only
    # https://stackoverflow.com/a/53070092/14558
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def __init__(self, model, admin_site):
        self.exclude = []

        # If the subclass already defined FOO_as_link in list_display, use that
        def maybe_link(field_name):
            if field_name + "_as_link" in self.list_display:
                self.exclude.append(field_name)
                return field_name + "_as_link"
            return field_name

        # Show all easily-displayable fields
        self.list_display = tuple(
            maybe_link(field.name)
            for field in model._meta.get_fields()
            if not field.many_to_many and not field.auto_created
        )
        self.list_select_related = True

        # This makes the _as_link function get used on the detail page
        self.readonly_fields = self.list_display

        field_names = [f.name for f in model._meta.get_fields()]
        if "id" in field_names:
            self.ordering = ["id"]

        if "text" in field_names:
            self.list_display_links += ("text",)

        super().__init__(model, admin_site)


def add_short_description(func, short_description):
    # There’s currently no reasonable way in mypy to declare attributes on
    # function objects
    # https://github.com/python/mypy/issues/2087
    func.short_description = short_description


@admin.register(Definition)
class DefinitionAdmin(CustomModelAdmin):
    list_display = ("wordform_as_link",)
    search_fields = ("text",)

    # “How to add clickable links to a field in Django admin?”:
    # https://stackoverflow.com/a/31745953/14558
    def wordform_as_link(self, obj: Definition):
        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.wordform),
            id=obj.wordform_id,
            name=str(obj.wordform),
        )

    add_short_description(wordform_as_link, "Wordform")


@admin.register(TargetLanguageKeyword)
class TargetLanguageKeywordAdmin(CustomModelAdmin):
    list_display = ("lemma_as_link",)
    search_fields = ("text",)

    def lemma_as_link(self, obj: Wordform):
        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.lemma),
            id=obj.lemma_id,
            name=str(obj.lemma),
        )

    add_short_description(lemma_as_link, "Lemma")


@admin.register(SourceLanguageKeyword)
class SourceLanguageKeywordAdmin(CustomModelAdmin):
    list_display = ("lemma_as_link",)
    search_fields = ("text",)

    def lemma_as_link(self, obj: Wordform):
        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.lemma),
            id=obj.lemma_id,
            name=str(obj.lemma),
        )

    add_short_description(lemma_as_link, "Lemma")


@admin.register(DictionarySource)
class DictionarySourceAdmin(CustomModelAdmin):
    pass


class DefinitionInline(admin.TabularInline):
    model = Definition
    show_change_link = True
    view_on_site = False


class TargetLanguageKeywordInline(admin.TabularInline):
    model = TargetLanguageKeyword
    show_change_link = True
    view_on_site = False


class SourceLanguageKeywordInline(admin.TabularInline):
    model = SourceLanguageKeyword
    show_change_link = True
    view_on_site = False


class WordformInline(admin.TabularInline):
    model = Wordform
    show_change_link = True
    verbose_name = "Inflection"
    verbose_name_plural = "Inflections"

    def get_view_on_site_url(self, obj=None):
        # get_absolute_url() throws exceptions if obj is not a lemma
        if obj.is_lemma:
            return obj.get_absolute_url()
        return None


@admin.register(Wordform)
class WordformAdmin(CustomModelAdmin):
    list_display = ("lemma_as_link",)
    search_fields = ("text", "analysis", "stem")
    list_filter = ("is_lemma",)

    inlines = [
        DefinitionInline,
        WordformInline,
        SourceLanguageKeywordInline,
        TargetLanguageKeywordInline,
    ]

    def view_on_site(self, obj):
        if obj.is_lemma:
            return obj.get_absolute_url()
        return None

    def lemma_as_link(self, obj: Wordform):
        if obj.lemma == obj:
            return "self"

        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.lemma),
            id=obj.lemma_id,
            name=str(obj.lemma),
        )

    add_short_description(lemma_as_link, "Lemma")
