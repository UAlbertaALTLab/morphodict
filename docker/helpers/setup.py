import re
from os import chmod, fspath, getuid
from pathlib import Path
from pwd import getpwuid
from shutil import chown
from subprocess import check_call

from .settings import APPS, DOCKER_COMPOSE_DIR

# Note the extra g+s bit. inode(7) says, “for that directory: files
# created there inherit their group ID from the directory, not from
# the effective group ID of the creating process”
GROUP_WRITABLE_DIR = 0o2775
GROUP_WRITABLE_FILE = 0o664


def do_setup(args):
    """Ensure required files and directories exist with correct permissions.

    Re-run this as the morphodict user at any time to make sure
    things are set up correctly.

    It assumes that users and base directories have already been created. That
    needs root permissions, and can be done via the ansible script in `plays/`.
    """
    assert (
        get_username() == "morphodict"
    ), "This script should be run as the morphodict user."

    setup_env_file()
    setup_dirs()
    setup_db()


def get_username():
    return getpwuid(getuid()).pw_name


def setup_dirs():
    for app in APPS:
        for data_mount in app.data_mounts():
            if data_mount.is_dir:
                src = Path(data_mount.prod_src)
                if not src.is_dir():
                    src.mkdir(GROUP_WRITABLE_DIR, exist_ok=True)
                chown(src, "morphodict", "morphodict-run")
                # Ths is subtle: the chmod has to come last, because running
                # chown clears the g+s bit, even if the user/group are the same
                # before and after.
                chmod(src, GROUP_WRITABLE_DIR)
            else:
                raise NotImplementedError(
                    "Non-directory mounts are not yet supported by this script"
                )

            print(data_mount, "ok")


def setup_db():
    for app in APPS:
        db_file = app.prod_db_file()

        # Enable SQLite write-ahead-logging mode. Makes the database
        # faster, with better concurrency support, at the cost of having
        # three files on disk when the database is open instead of only
        # one. This is safe for us to use with docker because we are
        # careful to mount a directory containing the SQLite database file,
        # instead of mounting just the database file by itself.
        #
        # See https://sqlite.org/wal.html
        check_call(
            [
                "sqlite3",
                fspath(db_file),
                "PRAGMA journal_mode=WAL",
            ]
        )

        chmod(db_file.parent, GROUP_WRITABLE_DIR)
        chown(db_file, "morphodict", "morphodict-run")
        chmod(db_file, GROUP_WRITABLE_FILE)
        print(f"{db_file} ok")


def setup_env_file():
    env_file = Path(DOCKER_COMPOSE_DIR / ".env")
    if not env_file.is_file():
        raise Exception(
            f"There is no file {env_file}. Either touch(1) it if this is a brand-new deploy, or copy the cookie-signing SECRET_KEY from an existing deploy. "
        )
    chmod(env_file, GROUP_WRITABLE_FILE)
    chown(env_file, "morphodict", "morphodict-run")

    # Set an environment variable to tell docker-compose to create containers
    # named morphodict_sssttt instead of docker_sssttt
    #
    # docker-compose automatically reads the .env file.
    env_file_contents = env_file.read_text()
    if not re.search("^COMPOSE_PROJECT_NAME=", env_file_contents, re.MULTILINE):
        env_file.write_text(env_file_contents + "\nCOMPOSE_PROJECT_NAME=morphodict\n")

    print(env_file, "ok")
