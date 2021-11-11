import pytest
from django.http import HttpRequest
from django.template import Context, RequestContext, Template
from pytest_django.asserts import assertInHTML


def test_produces_correct_markup():
    context = Context({"wordform": "wâpamêw"})
    template = Template("{% load morphodict_orth %}" "{{ wordform|orth:'Latn' }}")

    rendered = template.render(context)
    assert 'lang="cr"' in rendered
    assert 'data-orth-Latn="wâpamêw"' in rendered
    assert 'data-orth-Latn-x-macron="wāpamēw"' in rendered
    assert 'data-orth-Cans="ᐚᐸᒣᐤ"' in rendered
    assertInHTML(
        """
        <span lang="cr" data-orth
              data-orth-Latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-Cans="ᐚᐸᒣᐤ">wâpamêw</span>
        """,
        rendered,
    )


def test_naughty_html():
    """
    Does it escape bad HTML?
    """

    context = Context({"wordform": '<img alt="tâpwêw">'})
    template = Template("{% load morphodict_orth %}" "{{ wordform|orth:'Latn' }}")

    rendered = template.render(context)
    assertInHTML(
        """
        <span lang="cr" data-orth
              data-orth-Latn="&lt;img alt=&quot;tâpwêw&quot;&gt;"
              data-orth-latn-x-macron="&lt;img alt=&quot;tāpwēw&quot;&gt;"
              data-orth-Cans="&lt;img alt=&quot;ᑖᐻᐤ&quot;&gt;">&lt;img alt=&quot;tâpwêw&quot;&gt;</span>
        """,
        rendered,
    )


@pytest.mark.parametrize(
    "orth,inner_text",
    [
        ("Latn", "wâpamêw"),
        ("Latn-x-macron", "wāpamēw"),
        ("Cans", "ᐚᐸᒣᐤ"),
    ],
)
def test_provide_orthograpy(orth, inner_text):
    context = Context({"wordform": "wâpamêw"})
    template = Template(
        "{% load morphodict_orth %}" "{{ wordform|orth:" + repr(orth) + " }}"
    )

    rendered = template.render(context)
    assertInHTML(
        f"""
        <span lang="cr" data-orth
              data-orth-Latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-Cans="ᐚᐸᒣᐤ">{inner_text}</span>
        """,
        rendered,
    )


@pytest.mark.parametrize(
    "orth,inner_text",
    [
        ("Latn", "wâpamêw"),
        ("Latn-x-macron", "wāpamēw"),
        ("Cans", "ᐚᐸᒣᐤ"),
        (None, "wâpamêw"),  # use Latn if the cookie is not set in the request
    ],
)
def test_orth_template_tag(orth, inner_text):
    """
    Test that the {% orth %} tag uses the orthography in the request's cookie.
    """
    request = HttpRequest()
    if orth is not None:
        request.COOKIES["orth"] = orth

    context = RequestContext(request, {"wordform": "wâpamêw"})
    template = Template("{% load morphodict_orth %}" "{% orth wordform %}")
    rendered = template.render(context)

    assertInHTML(
        f"""
        <span lang="cr" data-orth
              data-orth-Latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-Cans="ᐚᐸᒣᐤ">{inner_text}</span>
        """,
        rendered,
    )


def test_cree_example():
    """
    Test the {% cree_example 'like: itwêwin' %} tag.
    """
    request = HttpRequest()
    request.COOKIES["orth"] = "Cans"

    context = RequestContext(request, {"example": "like: wâpamêw"})
    template = Template("{% load creedictionary_extras %}" "{% cree_example example %}")
    rendered = template.render(context)

    assertInHTML(
        f"""
        like: <span lang="cr" data-orth
              data-orth-Latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-Cans="ᐚᐸᒣᐤ">ᐚᐸᒣᐤ</span>
        """,
        rendered,
    )


@pytest.mark.parametrize(
    "orth,name",
    [("Latn", "SRO"), ("Latn-x-macron", "SRO"), ("Cans", "Syllabics"), (None, "SRO")],
)
def test_current_orthography_name_tag(orth, name):
    """
    Test that the {% current_orthography_name %} tag uses the orthography in the request's cookie.
    """
    request = HttpRequest()
    if orth is not None:
        request.COOKIES["orth"] = orth

    context = RequestContext(request)
    template = Template("{% load morphodict_orth %}" "{% current_orthography_name %}")
    rendered_html = template.render(context)
    assert name in rendered_html


def test_no_hyphens_in_syllabics():
    """
    Test that trailing hyphens disappear in syllabics.

    See: https://github.com/UAlbertaALTLab/morphodict/issues/314
    """
    context = Context({"wordform": "nôhtê-"})
    template = Template("{% load morphodict_orth %}" "{{ wordform|orth:'Cans' }}")

    rendered = template.render(context)
    assertInHTML(
        f"""
        <span lang="cr" data-orth
              data-orth-Latn="nôhtê-"
              data-orth-latn-x-macron="nōhtē-"
              data-orth-Cans="ᓅᐦᑌ">ᓅᐦᑌ</span>
        """,
        rendered,
    )


def test_url_for_query_tag():
    """
    Test that it works at all.
    """

    context = Context({"query": "wapamew"})
    template = Template("{% load creedictionary_extras %}" "{% url_for_query query %}")

    rendered = template.render(context)
    assert "search" in rendered
    assert "wapamew" in rendered


@pytest.mark.parametrize(
    ("orthography", "wordform"),
    [
        ("Latn", "wâpamêw"),
        ("Latn-x-macron", "wāpamēw"),
        ("Cans", "ᐚᐸᒣᐤ"),
    ],
)
def test_definition_link(db, orthography: str, wordform: str):
    """
    Test that it's in a link and the orthography is correct.
    """
    request = HttpRequest()
    request.COOKIES["orth"] = orthography
    context = RequestContext(request, {})
    template = Template(
        "{% load creedictionary_extras %}" '{% definition_link "wâpamêw" %}'
    )
    rendered = template.render(context)
    assert rendered.startswith("<a")
    assert rendered.endswith("</a>")
    assertInHTML(wordform, rendered)


@pytest.mark.parametrize(
    "wordform,classname",
    [
        ("ôma", "wordform--observed"),
        ("Fhqwhgads", "wordform--unobserved"),
    ],
)
def test_observed_or_unobserved(wordform: str, classname: str):
    context = Context({"wordform": wordform})
    template = Template(
        "{% load creedictionary_extras %}"
        "<span class='wordform--{% observed_or_unobserved wordform %}'>"
    )

    assert classname in template.render(context)
