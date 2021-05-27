"""
Access to relabelling from templates.
"""

import logging

from django import template

from CreeDictionary.CreeDictionary.relabelling import LABELS
from CreeDictionary.utils.types import FSTTag

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(takes_context=True)
def relabel(context, tags: tuple[FSTTag]):
    """
    Gets the best matching label for the given object.
    """
    # TODO: take in request context; relabel according to current label preference
    if label := LABELS.english.get_longest(tags):
        return label

    logger.warning("Could not find relabelling for tags: %r", tags)
    return "+".join(tags)
