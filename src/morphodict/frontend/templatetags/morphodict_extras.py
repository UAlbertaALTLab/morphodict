"""
Template tags related to the Cree Dictionary specifically.
"""

from urllib.parse import quote
from weakref import WeakKeyDictionary

from django import template
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from morphodict.search.crkeng_corpus_frequency import (
    observed_wordforms,
)
from morphodict.relabelling import read_labels
from morphodict.utils.views import url_for_query
from morphodict.orthography.templatetags.morphodict_orth import orth_tag
from morphodict.lexicon.models import Wordform

register = template.Library()


@register.simple_tag(takes_context=True)
def cree_example(context, example):
    """
    Similar to {% orth %}, but does not convert the 'like: ' prefix.
    This should be used for the examples given in crk.altlabel.tsv.

    e.g.,

        {% cree_example 'like: wâpamêw' %}

    Yields:

        like: <span lang="cr" data-orth
              data-orth-latn="wâpamêw"
              data-orth-latn-x-macron="wāpamēw"
              data-orth-cans="ᐚᐸᒣᐤ">wâpamêw</span>
    """
    if not example.startswith("like: "):
        # Do nothing if it doesn't look like an example
        return example

    _like, _sp, cree = example.partition(" ")
    return format_html("like: {}", orth_tag(context, cree))


@register.simple_tag(name="url_for_query")
def url_for_query_tag(user_query: str) -> str:
    """
    Same as url_for_query(query), but usable in a template:

    e.g.,

        {% url_for_query 'wâpamêw' %}

    yields:

        /search?q=w%C3%A2pam%C3%AAw
    """
    return url_for_query(user_query)


@register.simple_tag(takes_context=True)
def definition_link(context, slug: str) -> str:
    """
    Links to the definition of the wordform. Outputs wordform with current orthography.

    Warning: currently incurs a database query for every such link.
    """
    wordform = Wordform.objects.get(slug=slug)
    return format_html(
        '<a href="{}">{}</a>',
        reverse("dictionary-index-with-lemma", kwargs=dict(slug=slug)),
        orth_tag(context, wordform.text),
    )


@register.filter()
def kbd_text_query_link(text):
    """
    Link to a query URL, styling the query as keyboard input.

    Sample output:

        <a href="?text=foo"><kbd>foo</kbd></a>

    This is used on the fst-tool page.
    """
    return mark_safe(
        f"<a href='?text={escape(quote(text))}'><kbd>{escape(text)}</kbd></a>"
    )


@register.simple_tag()
def observed_or_unobserved(wordform: str):
    """
    Outputs the appropriate name depending on whether the word has been observed or not.
    This is intended to make the paradigm template a bit neater.

    Intended usage:

        <td "wordform wordform--{% observed_or_unobserved inflection.text %}">
    """
    if wordform in observed_wordforms():
        return "observed"
    return "unobserved"


PER_REQUEST_ID_COUNTER = WeakKeyDictionary()  # type: WeakKeyDictionary


@register.filter
def unique_id(request: HttpRequest) -> str:
    """
    Returns a new unique string that can be used as an id="" attribute in HTML.

    Usage:

    {% with new_id=request|unique_id %}
        <label for="input:{{ new_id }}"> I am labelling a far-away input </label>
            ...
        <input id="input:{{ new_id }}">
    {% endwith %}

    >>> req = HttpRequest()
    >>> tooltip1 = unique_id(req)
    >>> tooltip2 = unique_id(req)
    >>> tooltip1 == tooltip2
    False
    """

    generated_id = PER_REQUEST_ID_COUNTER.setdefault(request, 0)
    PER_REQUEST_ID_COUNTER[request] += 1

    return str(generated_id)


@register.simple_tag()
def relabel_plain_english(pos: str):
    """
    Should take in a class and return the plain english labelling for it
    So if I pass in "VTA-1", I should get back:
    like: wîcihêw
    """
    return read_labels().english.get(pos)


@register.simple_tag()
def relabel_source(pos: str):
    """
    Should take in a class and return the plain english labelling for it
    So if I pass in "VTA-1", I should get back:
    tâpiskôc: wîcihêw
    """
    return read_labels().source_language.get(pos)


@register.simple_tag()
def relabel_linguistic_short(pos: str):
    """
    Should take in a class and return the plain english labelling for it
    So if I pass in "VTA-1", I should get back:
    VTA-1
    """
    return read_labels().linguistic_short.get(pos)


@register.simple_tag()
def relabel_linguistic_long(pos: str):
    """
    Should take in a class and return the plain english labelling for it
    So if I pass in "VTA-1", I should get back:
    transitive animate verb – class 1: regular
    """
    return read_labels().linguistic_long.get(pos)


@register.filter()
def sort_sources(sources: list):
    """
    Should take in a class and return the plain english labelling for it
    So if I pass in "VTA-1", I should get back:
    transitive animate verb – class 1: regular
    """
    if "CW" in sources:
        sources.remove("CW")
        ret = ["CW"] + sources[:]
    else:
        ret = sources
    return ret

@register.filter(name="next")
def next(some_list, current_index):
    try:
        return some_list[int(current_index) + 1]
    except:
        return ''
    
@register.filter(name="has_next")
def has_next(some_list, current_index):
    return not current_index >= len(some_list) - 1
