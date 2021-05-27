"""
Add SVG sprites to your site!

See:
- https://css-tricks.com/svg-sprites-use-better-icon-fonts/
- https://css-tricks.com/svg-symbol-good-choice-icons/
- https://css-tricks.com/accessible-svg-icons-with-inline-sprites/

Usage:

    {% load svg_sprites %}

    {# Create your sprite sheet: #}
    {% load_svg_sprite "path/to/sprite.svg" "#svg-sprite-name" %}

    {# Now use your sprite! #}
    {% svg_sprite "#svg:sprite-name" %}
"""

import xml.etree.ElementTree as ET

from django.contrib.staticfiles.finders import find as find_static
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

SVG_NS = "http://www.w3.org/2000/svg"

register = template.Library()


@register.simple_tag
def load_svg_sprite(path: str, fragment: str):
    fragment = fragment.removeprefix("#")

    # get SVG from static files path
    svg_filepath = find_static(path)
    if svg_filepath is None:
        raise Exception("could not find file")

    tree = ET.parse(svg_filepath)
    root = tree.getroot()
    children = list(root)
    if len(children) == 0:
        raise NotImplementedError("empty image")
    if len(children) > 1:
        raise NotImplementedError("too many children")
    # TODO: create a <g> element for this
    first_element = children[0]
    first_element.attrib["id"] = fragment
    ET.register_namespace("", SVG_NS)
    svg = ET.tostring(first_element, encoding="unicode")

    viewbox = root.attrib["viewBox"]

    return format_html(
        "<svg "
        """aria-hidden="true" """
        """style="display:none" """
        """focusable="false" """
        f"""xmlns="{SVG_NS}" """
        ">"
        """<symbol id="{}" viewbox="{}">{}</symbol>"""
        "</svg>",
        fragment,
        viewbox,
        mark_safe(svg)
     )


@register.simple_tag
def svg_sprite(fragment: str):
    return format_html(
        '<svg><use xlink:href="#{}" /></svg>',
        fragment.removeprefix("#")
    )