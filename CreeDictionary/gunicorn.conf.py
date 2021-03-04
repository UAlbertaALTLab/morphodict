"""
Gunicorn configuration

This is used by default by the Docker image.

See: https://docs.gunicorn.org/en/stable/settings.html
"""

import os

# Allow ALL INTERFACES to connect to port 8000
bind = f"0.0.0.0:8000"

# Redirect output to errorlog
capture_output = True

loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
errorlog = "-"
accesslog = "-"
