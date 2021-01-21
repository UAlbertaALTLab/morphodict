from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Definition, DictionarySource, EnglishKeyword, Wordform


# https://stackoverflow.com/a/1720961/14558
def admin_url_for(obj):
    return reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=[obj.id],
    )


class CustomModelAdmin(admin.ModelAdmin):
    # https://stackoverflow.com/a/53070092/14558
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def __init__(self, model, admin_site):
        # If the subclass already defined FOO_as_link in list_display, use that
        def maybe_link(field_name):
            if field_name + "_as_link" in self.list_display:
                return field_name + "_as_link"
            return field_name

        self.list_display = tuple(
            maybe_link(field.name)
            for field in model._meta.get_fields()
            if not field.many_to_many and not field.auto_created
        )
        print(self.list_display)
        self.list_select_related = True

        field_names = [f.name for f in model._meta.get_fields()]
        if "id" in field_names:
            self.ordering = ["id"]

        if "text" in field_names:
            self.list_display_links += ("text",)

        super().__init__(model, admin_site)


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

    wordform_as_link.short_description = "Wordform"


@admin.register(EnglishKeyword)
class EnglishKeywordAdmin(CustomModelAdmin):
    list_display = ("lemma_as_link",)
    search_fields = ("text",)

    def lemma_as_link(self, obj: Wordform):
        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.lemma),
            id=obj.lemma_id,
            name=str(obj.lemma),
        )

    lemma_as_link.short_description = "Lemma"


@admin.register(DictionarySource)
class DictionarySourceAdmin(CustomModelAdmin):
    pass


@admin.register(Wordform)
class DictionarySourceAdmin(CustomModelAdmin):
    list_display = ("lemma_as_link",)
    search_fields = ("text", "analysis", "stem")

    def lemma_as_link(self, obj: Wordform):
        if obj.lemma == obj:
            return "self"

        return format_html(
            "<a href='{url}'>{id} {name}</a>",
            url=admin_url_for(obj.lemma),
            id=obj.lemma_id,
            name=str(obj.lemma),
        )

    lemma_as_link.short_description = "Lemma"
