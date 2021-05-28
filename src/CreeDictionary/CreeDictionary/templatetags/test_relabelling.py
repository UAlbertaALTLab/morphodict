from django.http import HttpRequest
from django.template import Context, RequestContext, Template

from CreeDictionary.CreeDictionary.paradigm.panes import RowLabel
from crkeng.app.preferences import ParadigmLabel


def test_relabel_tag():
    """
    Test that simple relabelling works.
    """
    # NOTE: this relies on the current contents of crk.altlabel.tsv
    # Its contents could change, so TRY to choose a label that is unlikely to change.
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    plain_english = "someone"

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
    request.COOKIES[ParadigmLabel.cookie_name] = "nehiyawewin"

    context = RequestContext(request, {"label": RowLabel(unspecified_actor)})
    template = Template("{% load relabelling %} {% relabel label.fst_tags %}")

    rendered = template.render(context)
    assert nehiyawewin in rendered.lower()
