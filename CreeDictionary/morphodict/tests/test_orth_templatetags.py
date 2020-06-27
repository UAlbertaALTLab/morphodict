#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pytest
from morphodict.templatetags.morphodict_orth import orth


def test_orth_requires_two_arguments():
    """
    orth() original only took one argument, but now it must take two.
    """
    with pytest.raises(TypeError):
        orth("wâpamêw")
