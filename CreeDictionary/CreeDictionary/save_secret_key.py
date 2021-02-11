import sys
from pathlib import Path


def save_secret_key(key: str) -> str:
    """
    Saves the secret key to the .env file.
    """
    env_file_path = _get_env_file_path()

    print("Secret key does not exist; saving to", env_file_path, file=sys.stderr)
    with env_file_path.open("a", encoding="UTF-8") as env_file:
        env_file.write(f"SECRET_KEY={key}\n")

    return key


def _get_env_file_path() -> Path:
    """
    Return the path to the .env file at the root of the repository assuming this
    structure:

    ./
    ├── .env
    └── CreeDictionary/
        └── CreeDictionary/
            └── save_secret_key.py

    """
    this_file = Path(__file__).resolve()
    # See: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.parents
    cree_dict_inner, cree_dict_outer, base_dir, *_ancestors = this_file.parents

    assert cree_dict_inner.name == "CreeDictionary"
    assert cree_dict_outer.name == "CreeDictionary"
    assert (base_dir / "pyproject.toml").is_file()
    return base_dir / ".env"
