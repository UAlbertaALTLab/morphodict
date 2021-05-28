"""
Preferences framework.

Allows for generic site-wide preferences stored in cookies.
"""


class Preference:
    cookie_name: str
    choices: list[str]
    default: str
