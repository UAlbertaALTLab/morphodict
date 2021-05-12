"""
Detect which host we're running on.
"""

import socket

HOSTNAME = socket.gethostname()
