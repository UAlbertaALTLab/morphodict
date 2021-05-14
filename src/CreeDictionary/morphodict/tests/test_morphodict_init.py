#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Some dummy tests just to make sure everything is working properly
"""

from django.apps import AppConfig


def test_default_config_exists():
    """
    A really trivial "test case": just checking that the app can be instantiated.
    """
    app = AppConfig.create("morphodict.apps.MorphodictConfig")
    assert "morphodict" in app.name
