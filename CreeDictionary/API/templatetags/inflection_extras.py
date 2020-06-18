import logging
from typing import Any, Union
from weakref import WeakKeyDictionary

from django import template
from django.forms import model_to_dict

from API.models import Wordform
from utils import crkeng_xml_utils, fst_analysis_parser
from utils.enums import WordClass

register = template.Library()


# custom filter one can use in template tags
@register.filter
def presentational_pos(wordform: Union[Wordform, dict]) -> str:
    """
    :param wordform_dict: a (maybe serialized) Wordform instance
    :return: a pos that is shown to users. like Noun, Verb, etc

    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "V", "inflectional_category": "VAI-v"})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "V", "inflectional_category": ""})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "", "inflectional_category": "VAI-v"})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "", "inflectional_category": ""})
    'Verb'
    """
    if isinstance(wordform, Wordform):
        wordform_dict = model_to_dict(wordform)
    elif isinstance(wordform, dict):
        wordform_dict = wordform
    else:
        raise TypeError

    # special case. In the source, some preverbs have pos labelled as IPC
    # e.g. for preverb "pe", the source gives pos=Ipc ic=IPV.
    inflectional_category = crkeng_xml_utils.convert_xml_inflectional_category_to_word_class(
        wordform_dict["inflectional_category"]
    )
    if inflectional_category is not None:
        if inflectional_category is WordClass.IPV:
            return "Preverb"

    pos = wordform_dict["pos"]
    if pos != "":
        if pos == "N":
            return "Noun"
        elif pos == "V":
            return "Verb"
        elif pos == "IPC":
            return "Particle"
        elif pos == "PRON":
            return "Pronoun"
        elif pos == "IPV":
            return "Preverb"

    if inflectional_category is None:
        inflectional_category = fst_analysis_parser.extract_word_class(
            wordform_dict["analysis"]
        )

    if inflectional_category is not None:
        if inflectional_category.is_noun():
            return "Noun"
        elif inflectional_category.is_verb():
            return "Verb"
        elif inflectional_category is WordClass.IPC:
            return "Ipc"
        elif inflectional_category is WordClass.Pron:
            return "Pronoun"
        elif inflectional_category is WordClass.IPV:
            return "Preverb"

    # fixme: where is this logged to in local development??? Does not show up in stdout/stderr for me.
    logging.error(
        f"can not determine presentational pos for {wordform_dict}, id={wordform_dict['id']}"
    )
    return ""


# XXX: mypy can't infer this type?
PER_REQUEST_ID_COUNTER = WeakKeyDictionary()  # type: WeakKeyDictionary


@register.filter
def unique_id(context: Any) -> str:
    """
    Returns a new unique string that can be used as an id="" attribute in HTML.

    Usage:

    {% with new_id=request|unique_id %}
        <label for="input:{{ new_id }}"> I am labelling a far-away input </label>
            ...
        <input id="input:{{ new_id }}">
    {% endwith %}

    >>> class Request:
    ...     pass
    ...
    >>> context = Request()
    >>> tooltip1 = unique_id(context)
    >>> tooltip2 = unique_id(context)
    >>> tooltip1 == tooltip2
    False
    """

    generated_id = PER_REQUEST_ID_COUNTER.setdefault(context, 0)
    PER_REQUEST_ID_COUNTER[context] += 1

    return str(generated_id)
