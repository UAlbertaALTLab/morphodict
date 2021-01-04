"""
This module provides utility that resolves our project paths listed in pyproject.toml
"""
import toml
from typing import Dict, Optional
from pathlib import Path
from os import path

FILE_DIR = Path(path.dirname(__file__))


def _get_project_root() -> Path:
    """
    bubbles up until we see a directory with .git folder

    :return: The root directory of the repository
    """
    # Uhh I actually don't know any reliable way to do this
    # this sounds like a reasonable method. You are Welcome to fix it.
    current = FILE_DIR
    while not (current / ".git").is_dir():
        current = current.parent
    return current


PROJECT_ROOT = _get_project_root()

_PROJECT_PATHS: Dict[str, Path] = {
    path_name: PROJECT_ROOT / Path(rel_path)
    for path_name, rel_path in toml.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text()
    )["project_paths"].items()
}


def get_project_path(name: str) -> Optional[Path]:
    """
    reads in project paths from pyproject.toml

    :param name: name as documented in pyproject.toml
    """
    return _PROJECT_PATHS.get(name)
