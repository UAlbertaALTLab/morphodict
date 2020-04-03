#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Settings for running within a Docker container.
"""

from pathlib import Path

from CreeDictionary.settings import *

# Where is data stored?
# This is a Docker volume:
DATA_DIR = Path("/data")

# Allow for easier local testing
ALLOWED_HOSTS += ["localhost"]

# Persist data to the mounted volume:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db.sqlite3"),
    }
}

log_dir = Path(DATA_DIR) / "log"
log_dir.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "handlers": {
        "write_debug_to_file_prod": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / "django.log"),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "filters": ["require_debug_false"],
        },
        "write_info_to_console_dev": {
            "level": "INFO",
            # without require_run_main_true, loggers from API.apps will print twice
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["write_debug_to_file_prod", "write_info_to_console_dev"],
            "level": "DEBUG",
        },
        # loggers created with logging.get_logger(__name__) under API app will use the configuration here
        "API": {
            "handlers": ["write_debug_to_file_prod", "write_info_to_console_dev"],
            "level": "DEBUG",
        },
    },
}
