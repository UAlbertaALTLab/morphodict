"""
check if we need to bump the version of @altlab/types package
The fact that this is only needed during github actions make me not place it under libexec directory.
"""
import argparse
import filecmp
import json
import sys
from difflib import context_diff
from pathlib import Path

parser = argparse.ArgumentParser(
    description="This script checks if our published types file and our current types file are the same."
                "If they are the same. Then we assert the package version hasn't changed."
                "Otherwise, we assert that the package version is different (which implies it has been bumped).")

parser.add_argument("current_package_dir")
parser.add_argument("published_package_dir")

args = parser.parse_args()

TYPES_FILE_NAME = "index.ts"

current_index_file = Path(args.current_package_dir) / TYPES_FILE_NAME
published_index_file = Path(args.published_package_dir) / TYPES_FILE_NAME

current_version: str = json.loads((Path(args.current_package_dir) / "package.json").read_text())["version"]
published_version: str = json.loads((Path(args.published_package_dir) / "package.json").read_text())["version"]

if filecmp.cmp(str(current_index_file), str(published_index_file)):
    # the case when the files are the same
    print("No change detected in API types file")
    sys.exit(0)
else:
    # the case when the files are different
    # then we expect the package version to change
    if current_version == published_version:

        # print diff to stderr and exit with 1
        with open(current_index_file) as f_a, open(published_index_file) as f_b:
            sys.stderr.writelines(
                context_diff(f_a.readlines(), f_b.readlines(), fromfile=args.file_a, tofile=args.file_b))
        print("API type file has changed. See the diff above.", file=sys.stderr)
        print(
            "Please bump types package version. "
            "Is the change a major change which breaks old interface,"
            " is it a backwards compatible feature, or it's a bug fix?)",
            file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(0)