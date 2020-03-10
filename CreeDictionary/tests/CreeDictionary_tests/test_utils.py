#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from string import printable as ascii_printable

import pytest
from CreeDictionary.utils import url_for_query


@pytest.mark.parametrize("query", ["awa", "wâpamêw", "ᐚᐸᒣᐤ"])
def test_query_always_ascii(query: str):
    url = url_for_query(query)
    assert all(
        c in ascii_printable for c in url
    ), f"{url!r} should not contain non-ascii characters"
