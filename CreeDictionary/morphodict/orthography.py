#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Handling of the writing system of the language.
"""

from typing import Set

from django.conf import settings


class Orthography:
    @property
    def default(self) -> str:
        return settings.MORPHODICT_ORTHOGRAPHY["default"]

    @property
    def available(self) -> Set[str]:
        return set(settings.MORPHODICT_ORTHOGRAPHY["available"].keys())

    def name_of(self, code: str) -> str:
        """
        Get the plain English name of the given orthography code.
        """
        return settings.MORPHODICT_ORTHOGRAPHY["available"][code]["name"]


ORTHOGRAPHY = Orthography()
