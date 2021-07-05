"""
Access to relabelling from templates.
"""

import logging
from typing import Sequence

from django import template
from django.template import Context

from CreeDictionary.CreeDictionary.relabelling import LABELS
from CreeDictionary.utils.types import FSTTag
from crkeng.app.preferences import ParadigmLabel

logger = logging.getLogger(__name__)
register = template.Library()

# If a paradigm label preference is not set, use this one!
DEFAULT_PARADIGM_LABEL = "english"

label_setting_to_relabeller = {
    "english": LABELS.english,
    "linguistic": LABELS.linguistic_short,
    "nehiyawewin": LABELS.cree,
}


@register.simple_tag(takes_context=True)
def relabel(context: Context, tags, labels=None):
    """
    Gets the best matching label for the given object.
    """

    if labels is None:
        label_setting = label_setting_from_context(context)
    else:
        label_setting = labels

    if isinstance(tags, str):
        tags = (tags,)

    relabeller = label_setting_to_relabeller[label_setting]

    if label := relabeller.get_longest(tags):
        return label

    logger.warning("Could not find relabelling for tags: %r", tags)
    return "+".join(tags)


def label_setting_from_context(context: Context):
    """
    Returns the most appropriate paradigm label preference.
    :param context: a simple template Context or a RequestContext
    """
    if hasattr(context, "request"):
        # We can get the paradigm label from the cookie!
        return context.request.COOKIES.get(
            ParadigmLabel.cookie_name, ParadigmLabel.default
        )

    # Cannot get the request context? We can't detect the current cookie :/
    return ParadigmLabel.default
