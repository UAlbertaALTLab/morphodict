"""
Display options. Currently controls:

 - "mode": either "basic" and "traditional"

As of 2021-04-14, "mode" is a corse mechanism for affecting the display; there are a
plans for more fine-grained control over the display of, e.g., search results.
"""


DISPLAY_MODE_COOKIE = "mode"
DISPLAY_MODES = {
    # Community-mode: uses emoji and hides inflectional class
    "community",
    # Linguist-mode: always displays inflectional class (e.g., VTA-1, NA-3, IPJ, etc.)
    "linguistic",
}
DEFAULT_DISPLAY_MODE = "community"