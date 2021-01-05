#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Configuration for gunicorn on Sapir.

It's recommended to use the GUNICORN_* environment variables to further configure this!
"""

import os
from pathlib import Path

PORT = os.getenv("PORT", "8000")
log_prefix = Path(os.getenv("GUNICORN_LOG_PREFIX", "/var/log/cree-dictionary"))

bind = f"0.0.0.0:{PORT}"

workers = int(os.getenv("GUNICORN_WORKERS", 3))

capture_output = True
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log = Path(os.getenv("GUNICORN_ACCESS_LOG", log_prefix / "access.log"))
error_log = Path(os.getenv("GUNICORN_ACCESS_LOG", log_prefix / "error.log"))
