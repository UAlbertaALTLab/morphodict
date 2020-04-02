#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Detect which host we're running on.
"""

import socket

_SAPIR_HOSTNAME = "arrl-web003"
HOSTNAME = socket.gethostname()
HOST_IS_SAPIR = HOSTNAME == _SAPIR_HOSTNAME
