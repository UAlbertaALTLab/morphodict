from django.http import HttpRequest
from django.template import Context, RequestContext, Template

from CreeDictionary.CreeDictionary.paradigm.panes import RowLabel
from crkeng.app.preferences import DisplayMode


def test_relabel_tag():
    """
    Test that simple relabelling works.
    """
    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    plain_english = "people"

    context = Context({"label": RowLabel(unspecified_actor)})
    template = Template("{% load relabelling %} {% relabel label.fst_tags %}")

    rendered = template.render(context)
    assert plain_english in rendered.lower()


def test_relabel_tag_uses_cookie():
    """
    Test that simple relabelling works.
    """
    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    nehiyawewin = "awiya"

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = "source_language"

    context = RequestContext(request, {"label": RowLabel(unspecified_actor)})
    template = Template("{% load relabelling %} {% relabel label.fst_tags %}")

    rendered = template.render(context)
    assert nehiyawewin in rendered.lower()


def test_relabel_tag_ignores_bad_cookie():
    """
    Test that simple relabelling works.
    """
    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    english = "people"

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = "totally-invalid-value-🐐"

    context = RequestContext(request, {"label": RowLabel(unspecified_actor)})
    template = Template("{% load relabelling %} {% relabel label.fst_tags %}")

    rendered = template.render(context)
    assert english in rendered.lower()


def test_relabel_tag_with_explict_label_setting() -> None:
    """
    Test relabeling providing an explicit label setting.
    """

    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    plain_english = "people"
    nehiyawewin = "awiya"

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = "source_language"

    context = RequestContext(request, {"label": RowLabel(unspecified_actor)})

    template_from_context = Template(
        "{% load relabelling %} {% relabel label.fst_tags %}"
    )
    rendered_from_context = template_from_context.render(context).lower()
    assert nehiyawewin in rendered_from_context
    assert plain_english not in rendered_from_context

    template_with_argument = Template(
        "{% load relabelling %} {% relabel label.fst_tags labels='english' %}"
    )
    rendered_with_argument = template_with_argument.render(context).lower()
    assert plain_english in rendered_with_argument
    assert nehiyawewin not in rendered_with_argument


def test_relabel_one_tag() -> None:
    """
    Test that {% relabel_one tag %} is identical to {% relabel (tag,) %}
    """

    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    unspecified_actor_tag = "X"

    request = HttpRequest()
    request.COOKIES[DisplayMode.cookie_name] = "source_language"

    context = RequestContext(
        request, {"label": RowLabel(unspecified_actor), "tag": unspecified_actor_tag}
    )

    template_with_relabel = Template(
        "{% load relabelling %} {% relabel label.fst_tags %}"
    )
    template_with_relabel_one = Template("{% load relabelling %} {% relabel_one tag %}")
    rendered_with_relabel = template_with_relabel.render(context).lower()
    rendered_with_relabel_one = template_with_relabel_one.render(context).lower()

    assert rendered_with_relabel_one == rendered_with_relabel
