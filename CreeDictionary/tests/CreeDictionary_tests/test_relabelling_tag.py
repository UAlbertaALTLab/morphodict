from django.template import Context, Template

from CreeDictionary.paradigm.panes import RowLabel


def test_relabel_tag():
    """
    Test that simple relabelling works.
    """
    # XXX: note, this relies on the current contents of crk.altlabel.tsv;
    # the contents could change, so try to choose a label that... is unlikely to change?
    # I guess both the tag and label for "unspecified actor" are unlikely to change, so:
    unspecified_actor = ("X",)
    plain_english = "someone"
    context = Context({"label": RowLabel(unspecified_actor)})
    template = Template("{% load relabelling %}" "{% relabel label.fst_tags %}")

    rendered = template.render(context)
    assert plain_english in rendered.lower()
