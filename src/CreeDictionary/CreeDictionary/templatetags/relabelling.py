"""
Access to relabelling from templates.
"""

from django import template

from CreeDictionary.CreeDictionary.relabelling import LABELS
from CreeDictionary.utils.types import FSTTag

register = template.Library()


@register.simple_tag
def relabel(thing: tuple[FSTTag]):
    """
    Gets the best matching label for the given object.
    """
    # TODO: take in request context; relabel according to current label preference
    return LABELS.english.get_longest(thing)
