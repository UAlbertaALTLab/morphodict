#!/usr/bin/env python3

# Fun fact! This started as a shell script but the .py extension confused black.
import os
import sys
from pathlib import Path
from shutil import which

dir = Path(__file__).parent

docker_compose = which("docker-compose")

os.execv(
    docker_compose,
    [
        docker_compose,
        # By passing the full path to the yml, the current wrapper script
        # can be called from any working directory
        "-f",
        dir.absolute() / "docker-compose.yml",
        "exec",
        "app",
        "/app/.venv/bin/python",
        "./manage.py",
    ]
    + sys.argv[1:],
)
