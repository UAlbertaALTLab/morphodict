import re
from os import chmod
from pathlib import Path
from shutil import chown

from .settings import APPS, DIR


def do_setup(args):
    """Create unprivileged files and directories required by deployment.

    This assumes that users and base directories have already been created.
    That needs root permissions, and can be done via the ansible script in
    `plays/`.
    """
    GROUP_WRITABLE_DIR = 0o775
    GROUP_WRITABLE_FILE = 0o664

    env_file = Path(DIR / ".env")
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
    if not re.match("^COMPOSE_PROJECT_NAME=", env_file_contents, re.MULTILINE):
        env_file.write_text(env_file_contents + "\nCOMPOSE_PROJECT_NAME=morphodict\n")

    print(env_file, "ok")

    for app in APPS:
        for data_mount in app.data_mounts():
            if data_mount.is_dir:
                src = Path(data_mount.prod_src)
                if not src.is_dir():
                    src.mkdir(GROUP_WRITABLE_DIR, exist_ok=True)
                else:
                    chmod(src, GROUP_WRITABLE_DIR)
                chown(src, "morphodict", "morphodict-run")
            else:
                raise NotImplementedError("no non-dir mount support yet")

            print(data_mount, "ok")
