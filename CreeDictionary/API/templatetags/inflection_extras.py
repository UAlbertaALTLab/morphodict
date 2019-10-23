from typing import Optional

from django import template

from API.models import Inflection
from constants import LC
from utils import fst_analysis_parser

register = template.Library()


# custom filter one can use in template tags
@register.filter
def presentational_pos(inflection: Inflection):
    """
    :return: a pos that is shown to users. like Noun, Verb, etc
    """
    if inflection.pos != "":
        if inflection.pos == "N":
            return "Noun"
        elif inflection.pos == "V":
            return "Verb"
        elif inflection.pos == "IPC":
            return "Ipc"
        elif inflection.pos == "PRON":
            return "Pronoun"
        elif inflection.pos == "IPV":
            return "Ipv"

    lc: Optional[LC]
    if inflection.lc != "":
        lc = LC(inflection.lc)
    else:
        lc = fst_analysis_parser.extract_category(inflection.analysis)
    if lc is not None:
        if lc.is_noun():
            return "Noun"
        elif lc.is_verb():
            return "Verb"
        elif lc is LC.IPC:
            return "Ipc"
        elif lc is LC.Pron:
            return "Pronoun"

    raise ValueError(
        f"can not determine presentational pos for {inflection}, id={inflection.id}"
    )
