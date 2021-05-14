from typing import Any
from weakref import WeakKeyDictionary

from django import template

register = template.Library()


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
