import hashlib
import logging
import os
import shutil
import subprocess
from argparse import ArgumentParser, BooleanOptionalAction, RawDescriptionHelpFormatter
from pathlib import Path
from subprocess import check_call
from time import strftime
from typing import Optional

from django.core.management import BaseCommand

from ... import DEFAULT_SAMPLE_FILE

logger = logging.getLogger(__name__)


class BranchSpecification:
    def __init__(self, branch_name):
        self.name = branch_name

    name: str
    checkout_dir: Optional[str]
    revision: Optional[str]

    def ensure_checkout_exists(self, main_git_repo):
        if not (self.checkout_dir / ".git").exists():
            logger.info(f"{self.checkout_dir} does not exist, cloning")
            self.checkout_dir.parent.mkdir(exist_ok=True)

            check_call(
                [
                    "git",
                    "clone",
                    main_git_repo,
                    "--shared",  # share blob storage with current repo
                    "--branch",
                    self.name,
                    self.name,
                ],
                cwd=self.checkout_dir.parent,
            )

    def reset_hard(self):
        self.check_call_in_dir(["git", "reset", "--hard", self.revision])

    def check_call_in_dir(self, *args, **kwargs):
        logger.info(f"Running {args}")

        # Make sure we are running in the correct dir
        kwargs2 = dict(kwargs)
        kwargs2["cwd"] = self.checkout_dir

        env = dict(os.environ)
        # Don’t re-use parent virtualenv
        env["PIPENV_IGNORE_VIRTUALENVS"] = "1"
        # Don’t use the test DB
        env["USE_TEST_DB"] = "False"
        kwargs2["env"] = env

        return check_call(*args, **kwargs2)

    def setup_package_managers(self):
        self.check_call_in_dir(["pipenv", "install", "--dev"])
        # If the Pipfile has changed since the last run, `install` does
        # *not* remove any now-extraneous packages
        self.check_call_in_dir(["pipenv", "clean"])

    def build_dictionary_if_needed(self, crkeng_xml):
        db_file = self.checkout_dir / "CreeDictionary" / "db.sqlite3"

        if db_file.exists():
            # The file exists, but might it be useful?
            stat = db_file.stat()
            if stat.st_size < 100_000_000:
                logger.info(f"{db_file} exists but is too small to be valid, removing")
                db_file.unlink()
            else:
                logger.info(f"{db_file} exists, not building")
                return

        try:
            self.check_call_in_dir(
                ["pipenv", "run", "python", "CreeDictionary/manage.py", "migrate"]
            )
            self._do_build_db(crkeng_xml)
        except Exception:
            # If building the DB failed, remove it so that there isn’t a file to
            # mislead us into thinking there’s a valid database on the next run.
            if db_file.exists():
                db_file.unlink()
            raise

    def _do_build_db(self, crkeng_xml):
        """
        Do the actual database build

        How to build the DB has changed over time, so provide an overrideable
        method.
        """
        logger.info("In parent method")
        self.check_call_in_dir(
            [
                "pipenv",
                "run",
                "python",
                "CreeDictionary/manage.py",
                "xmlimport",
                crkeng_xml,
            ]
        )


class DatabaseManagerUsingImportBranchSpecification(BranchSpecification):
    def __init__(self, branch_name, database_manager_module_name):
        super().__init__(branch_name=branch_name)
        self.database_manager_module_name = database_manager_module_name

    def _do_build_db(self, crkeng_xml):
        logger.info("In child method")
        self.check_call_in_dir(
            [
                "pipenv",
                "run",
                "python",
                "-m",
                self.database_manager_module_name,
                "import",
                crkeng_xml.parent,
            ]
        )


BRANCHES = [
    # Note: marisa-trie segfaults on Ubuntu 20.10 due to this GCC bug:
    # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=99375
    # My workaround was to build python 3.6.13 with CC=clang
    DatabaseManagerUsingImportBranchSpecification(
        branch_name="v2020", database_manager_module_name="DatabaseManager.__main__"
    ),
    DatabaseManagerUsingImportBranchSpecification(
        branch_name="v2021-01-25-post-dupe",
        database_manager_module_name="DatabaseManager.main",
    ),
    BranchSpecification(branch_name="main"),
]

DEFAULT_BRANCHES = [b.name for b in BRANCHES]


def find_branch(branch_name):
    """Return the matching branch from BRANCHES, or raise"""
    matches = [b for b in BRANCHES if b.name == branch_name]
    if len(matches) > 1:
        raise Exception(f"Multiple specifications for {branch_name}")
    if len(matches) == 0:
        raise Exception(f"No specification for {branch_name}")
    return matches[0]


def check_output_str(param, cwd):
    """Run check_output, but return a string, and without trailing newlines"""
    output = subprocess.check_output(param).decode("UTF-8")
    while output.endswith("\n"):
        output = output[:-1]
    return output


def git_blob_style_hash(data: bytes):
    """Return the hash of data as a hex string

    This is the hash that git uses for hashing blobs. You can pass the hash
    returned by this function to git to find a copy of the file in the history
    of a repository, for example

        git whatchanged --all --find-object=acab3218a50a

    >>> git_blob_style_hash(b'hi\\n')
    '45b983be36b73c0788dc9cbcb76cbb80fc7bb057'
    """
    hash = hashlib.sha1()
    hash.update(b"blob %d\0" % len(data))
    hash.update(data)
    return hash.hexdigest()


class Command(BaseCommand):
    help = """
        Run sample queries across multiple branches

        When the list of search queries we are using for evaluation changes, in
        order to see how older code performed on the newly-selected queries, we
        need to regenerate the search results by running queries against old
        versions of the code. That’s what this script does.

        Note that this only needs to be done when query terms are added; changes
        in expected results do not require re-running, as evaluation is
        performed against saved search results in the query-results.json.gz
        files.
        """

    def add_arguments(self, parser: ArgumentParser):
        parser.formatter_class = RawDescriptionHelpFormatter
        parser.add_argument("--csv-file", default=DEFAULT_SAMPLE_FILE)
        parser.add_argument(
            "--branch-checkout-dir",
            default=Path("~/alt/sample-query-branches").expanduser(),
            help="A directory in which to store branch checkouts and databases",
        )
        parser.add_argument(
            "--altlab-repo-checkout-dir",
            default=Path("~/alt/git/altlab").expanduser(),
            help="Path to checkout of git repo containing full crkeng.xml; clone it from altlab.dev:/data/altlab.git",
        )
        parser.add_argument(
            "--re-run",
            action=BooleanOptionalAction,
            default=False,
            help="re-run even if sample file, with sample.csv hash in name, already exists",
        )
        parser.add_argument(
            "--branch",
            action="append",
            default=[],
            help=f"Which branch(es) to run against, default={DEFAULT_BRANCHES}",
        )

    def handle(self, *args, **options) -> None:
        raise NotImplementedError("Still dependent on CreeDictionary code")
        if not options["branch"]:
            options["branch"] = DEFAULT_BRANCHES

        sample_csv_file = Path(options["csv_file"])

        sample_csv_hash = git_blob_style_hash(sample_csv_file.read_bytes())[:12]
        date = strftime("%Y-%m-%d")
        results_base_name = f"{date}-{sample_csv_hash}"

        script_dir = Path(__file__).parent

        main_git_repo = check_output_str(
            ["git", "rev-parse", "--show-toplevel"], cwd=script_dir
        )

        for branch_name in options["branch"]:
            branch = find_branch(branch_name)

            logger.info(f"Working on branch {branch.name}")

            branch.revision = check_output_str(
                ["git", "rev-parse", branch.name], cwd=script_dir
            )
            branch.checkout_dir = Path(options["branch_checkout_dir"] / branch.name)

            branch.ensure_checkout_exists(main_git_repo)
            branch.reset_hard()

            shutil.copy(
                sample_csv_file,
                branch.checkout_dir / "morphodict" / "search_quality" / "sample.csv",
            )

            branch.setup_package_managers()
            branch.build_dictionary_if_needed(
                crkeng_xml=Path(options["altlab_repo_checkout_dir"])
                / "crk"
                / "dicts"
                / "crkeng.xml"
            )

            output_file = (
                script_dir
                / ".."
                / ".."
                / "sample_results"
                / f"{results_base_name}-{branch.name}.json.gz"
            ).absolute()

            if output_file.exists() and not options["re_run"]:
                continue

            branch.check_call_in_dir(
                [
                    "pipenv",
                    "run",
                    "python",
                    "CreeDictionary/manage.py",
                    "runsamplequeries",
                    "--query-results-file",
                    output_file,
                ]
            )
