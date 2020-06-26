#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Handling of the writing system of the language.
"""

from typing import Set

from utils import ORTHOGRAPHY_NAME as _ORTHOGRAPHY_NAME
from utils.vars import DEFAULT_ORTHOGRAPHY as _DEFAULT_ORTHOGRAPHY


class Orthography:
    # TODO:
    default = _DEFAULT_ORTHOGRAPHY

    @property
    def available(self) -> Set[str]:
        return set(_ORTHOGRAPHY_NAME.keys())


ORTHOGRAPHY = Orthography()
