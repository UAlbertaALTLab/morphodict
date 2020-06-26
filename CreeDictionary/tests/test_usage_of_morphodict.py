#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from morphodict.orthography import ORTHOGRAPHY


def test_morphodict_orthography():
    assert ORTHOGRAPHY.default == "Latn"
    assert {"Latn", "Cans", "Latn-x-macron"} <= set(ORTHOGRAPHY.available)
