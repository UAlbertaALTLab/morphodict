#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Handling of the writing system of the language.
"""

from typing import Set

from utils import ORTHOGRAPHY_NAME as _ORTHOGRAPHY_NAME
from utils.vars import DEFAULT_ORTHOGRAPHY as _DEFAULT_ORTHOGRAPHY


class Orthography:
    # TODO: get from settings
    default = _DEFAULT_ORTHOGRAPHY

    @property
    def available(self) -> Set[str]:
        # TODO: get from settings
        return set(_ORTHOGRAPHY_NAME.keys())


ORTHOGRAPHY = Orthography()
