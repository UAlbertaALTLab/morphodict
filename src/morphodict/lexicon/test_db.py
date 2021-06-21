# This file contains code for dealing with the test database, not for testing
# the database.
from morphodict import morphodict_language_pair
from morphodict.lexicon import DICTIONARY_RESOURCE_DIR

TEST_DB_IMPORTJSON = DICTIONARY_RESOURCE_DIR / (
    morphodict_language_pair() + "_test_db.importjson"
)

TEST_DB_TXT_FILE = DICTIONARY_RESOURCE_DIR / "test_db_words.txt"


def get_test_words() -> set[str]:
    """
    get manually specified test words from res/test_db_words.txt
    """
    lines = TEST_DB_TXT_FILE.read_text().splitlines()
    words = set()
    for line in lines:
        line = line.strip()
        if line and line[0] != "#":
            words.add(line)

    return words
