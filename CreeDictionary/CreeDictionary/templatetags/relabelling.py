"""
Access to relabelling from templates.
"""

from django import template
from utils.types import FSTTag

from CreeDictionary.relabelling import LABELS

register = template.Library()


@register.simple_tag
def relabel(thing: tuple[FSTTag]):
    """
    Gets the best matching label for the given object.
    """
    # TODO: take in request context; relabel according to current label preference
    return LABELS.english.get_longest(thing)
