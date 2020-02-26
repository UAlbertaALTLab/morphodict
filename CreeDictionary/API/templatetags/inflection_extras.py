import logging
from typing import Union

from django import template
from django.forms import model_to_dict

from API.models import Wordform
from constants import SimpleLC
from utils import fst_analysis_parser, crkeng_xml_utils

register = template.Library()


# custom filter one can use in template tags
@register.filter
def presentational_pos(wordform: Union[Wordform, dict]) -> str:
    """
    :param wordform_dict: a (maybe serialized) Wordform instance
    :return: a pos that is shown to users. like Noun, Verb, etc

    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "V", "full_lc": "VAI-v"})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "V", "full_lc": ""})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "", "full_lc": "VAI-v"})
    'Verb'
    >>> presentational_pos({"analysis": "nipâw+V+AI+Ind+Prs+3Sg", "pos": "", "full_lc": ""})
    'Verb'
    """
    if isinstance(wordform, Wordform):
        wordform_dict = model_to_dict(wordform)
    elif isinstance(wordform, dict):
        wordform_dict = wordform
    else:
        raise TypeError

    # special case. In the source, some preverbs have pos labelled as IPC
    # e.g. for preverb "pe", the source gives pos=Ipc lc=IPV.
    lc = crkeng_xml_utils.parse_xml_lc(wordform_dict["full_lc"])
    if lc is not None:
        if lc is SimpleLC.IPV:
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

    if lc is None:
        lc = fst_analysis_parser.extract_simple_lc(wordform_dict["analysis"])

    if lc is not None:
        if lc.is_noun():
            return "Noun"
        elif lc.is_verb():
            return "Verb"
        elif lc is SimpleLC.IPC:
            return "Ipc"
        elif lc is SimpleLC.Pron:
            return "Pronoun"
        elif lc is SimpleLC.IPV:
            return "Preverb"

    logging.error(
        f"can not determine presentational pos for {wordform_dict}, id={wordform_dict.id}"
    )
    return ""
