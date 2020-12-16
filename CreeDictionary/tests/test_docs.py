from pathlib import Path
from gitignore_parser import parse_gitignore
from os import path
import os
from typing import List, Callable, NoReturn
import toml
import pytest
from sys import stderr
from functools import partial
from sortedcontainers import SortedSet

IgnoreCheck = Callable[[Path], bool]
"""
If a path is ignored, it gives True. If a path is not ignored, it gives False
"""

FILE_DIR = Path(path.dirname(__file__))


def get_project_root():
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


PROJECT_ROOT = get_project_root()


def _get_not_ignored_dirs(root: Path, ancestral_ignores: List[IgnoreCheck]) -> List[Path]:
    """
    :param root: must be a existent directory
    :return: all dirs that are not gitignored, not including root. sorted in a depth first manner
    """
    # .is_dir also checks existence
    assert root.is_dir(), "dumb dumb: root must be a directory :broken_heart:"

    ret = []

    ignores_in_control = ancestral_ignores.copy()

    # is_file also checks for existence
    for own_ignore in filter(Path.is_file, [root / ".gitignore", root / ".dirdocignore"]):
        ignores_in_control.append(parse_gitignore(own_ignore))

    # glob('*') returns direct children only
    for child_dir in filter(Path.is_dir, root.glob("*")):
        # for/else is used by intention here for early return pattern
        for ignore in ignores_in_control:
            if ignore(child_dir):
                break
        else:  # not ignored
            ret.append(child_dir)
            ret.extend(_get_not_ignored_dirs(child_dir, ignores_in_control))

    return ret


def get_not_ignored_dirs() -> List[Path]:
    """
    get all directories in this project that are not included in .gitignore or .dirdocignore
    """
    return _get_not_ignored_dirs(PROJECT_ROOT, [])


def fail_and_provide_suggestion(reason: str, suggestion: str):
    print(reason, file=stderr)
    print(suggestion, file=stderr)
    pytest.fail(reason)


def format_as_lines_relative_to_project(paths: List[Path], as_md_header: bool=False) -> str:
    """
    :param paths: absolute paths
    :param as_md_header: if True, adds ### to each Path
    :return: a string of lines, where each line ends with \n
    """
    ret = ""
    for p in paths:
        if as_md_header:
            ret += "###"
        ret += str(p.relative_to(PROJECT_ROOT)) + "\n"

    return ret


def test_dirs_get_docs():
    parsed_tml = toml.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    # if we were to use vallina set, the suggestions would come out in allphabetical order
    # which makes less sense than depth first order in terms of directory presentation
    ones_with_docs = SortedSet()
    non_existent_dirs = SortedSet()
    non_dir_docs = SortedSet()

    doc_file = Path(PROJECT_ROOT / parsed_tml["tool"]["dirdoc"]["doc_file"])
    for line in doc_file.read_text().splitlines():
        if line.lstrip().startswith("###"):
            dir_with_doc = Path(PROJECT_ROOT / line.partition("###")[2].strip())
            if (not dir_with_doc.exists()):
                non_existent_dirs.add(dir_with_doc)
            if (not dir_with_doc.is_dir()):
                non_dir_docs.add(dir_with_doc)
            ones_with_docs.add(dir_with_doc)

    failing_reason = ""
    failing_suggestion = ""
    if len(non_existent_dirs) != 0:
        failing_reason += f"{len(non_existent_dirs)} non existent entrie(s) found in {doc_file.relative_to(PROJECT_ROOT)}\n"
        failing_suggestion += "Could you delete the following entries? :\n"
        failing_suggestion += format_as_lines_relative_to_project(non_existent_dirs)
    if len(non_dir_docs) != 0:
        failing_reason += f"{len(non_dir_docs)} entrie(s) found in {doc_file.relative_to(PROJECT_ROOT)} are not directories\n"
        failing_suggestion += "Could you delete the following entries? :\n"
        failing_suggestion += format_as_lines_relative_to_project(non_dir_docs)


    not_ignored_dirs = SortedSet(get_not_ignored_dirs())
    lacking_dirs = not_ignored_dirs - ones_with_docs


    if len(lacking_dirs) != 0:
        failing_reason += f"{len(lacking_dirs)} directories are missing documentation. Consider adding them to .dirdocignore or add the entries inside {doc_file.relative_to(PROJECT_ROOT)}"

        failing_suggestion += f"Consider adding the following entries inside {doc_file.relative_to(PROJECT_ROOT)}:" + \
                              "todo: document about directories\n" + \
                              format_as_lines_relative_to_project(lacking_dirs, as_md_header=True)

    extra_dirs = ones_with_docs - not_ignored_dirs
    if len(extra_dirs) != 0:
        failing_reason += f"{len(extra_dirs)} directories are ignored but existent in {doc_file.relative_to(PROJECT_ROOT)}. Consider deleting them"

        failing_suggestion += f"Consider deleting following entries inside {doc_file.relative_to(PROJECT_ROOT)}:\n" + \
                              format_as_lines_relative_to_project(extra_dirs, as_md_header=True)


    if failing_reason != "":
        fail_and_provide_suggestion("\n" + failing_reason, "\n" + failing_suggestion)
