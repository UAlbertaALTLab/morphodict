#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Detect which host we're running on.
"""

import socket

HOSTNAME = socket.gethostname()
