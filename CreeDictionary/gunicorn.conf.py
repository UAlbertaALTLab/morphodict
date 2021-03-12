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

workers = 3

# Log level is documented as lowercase for some reason:
# See: https://docs.gunicorn.org/en/stable/settings.html#loglevel
loglevel = os.getenv("LOG_LEVEL", "info").lower()
errorlog = "-"
accesslog = "-"
