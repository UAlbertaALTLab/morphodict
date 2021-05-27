"""
Access to relabelling from templates.
"""

import logging

from django import template

from CreeDictionary.CreeDictionary.relabelling import LABELS
from CreeDictionary.utils.types import FSTTag
from crkeng.app.views import PARADIGM_LABEL_COOKIE

logger = logging.getLogger(__name__)
register = template.Library()

# If a paradigm label prefernece is not set, use this one!
DEFAULT_PARADIGM_LABEL = "english"

label_setting_to_relabeller = {
    "english": LABELS.english,
    "linguistic": LABELS.linguistic_short,
    "nehiyawewin": LABELS.cree,
}


@register.simple_tag(takes_context=True)
def relabel(context, tags: tuple[FSTTag]):
    """
    Gets the best matching label for the given object.
    """

    if hasattr(context, "request"):
        # we can get the paradigm label from the cookie!
        label_setting = context.request.COOKIES.get(
            PARADIGM_LABEL_COOKIE, DEFAULT_PARADIGM_LABEL
        )
    else:
        # Cannot get the request context? We can't detect the current cookie :/
        label_setting = DEFAULT_PARADIGM_LABEL

    relabeller = label_setting_to_relabeller[label_setting]

    # TODO: take in request context; relabel according to current label preference
    if label := relabeller.get_longest(tags):
        return label

    logger.warning("Could not find relabelling for tags: %r", tags)
    return "+".join(tags)
