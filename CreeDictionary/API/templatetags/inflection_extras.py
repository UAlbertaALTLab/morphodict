import logging
from typing import Optional

from django import template

from API.models import Wordform
from constants import SimpleLC
from utils import fst_analysis_parser, crkeng_xml_utils

register = template.Library()


# custom filter one can use in template tags
@register.filter
def presentational_pos(wordform: Wordform):
    """
    :return: a pos that is shown to users. like Noun, Verb, etc
    """

    # special case. In the source, some preverbs have pos labelled as IPC
    # e.g. for preverb "pe", the source gives pos=Ipc lc=IPV.
    lc = crkeng_xml_utils.parse_xml_lc(wordform.full_lc)
    if lc is not None:
        if lc is SimpleLC.IPV:
            return "Preverb"

    if wordform.pos != "":
        if wordform.pos == "N":
            return "Noun"
        elif wordform.pos == "V":
            return "Verb"
        elif wordform.pos == "IPC":
            return "Particle"
        elif wordform.pos == "PRON":
            return "Pronoun"
        elif wordform.pos == "IPV":
            return "Preverb"

    if lc is None:
        lc = fst_analysis_parser.extract_simple_lc(wordform.analysis)

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
        f"can not determine presentational pos for {wordform}, id={wordform.id}"
    )
    return ""
