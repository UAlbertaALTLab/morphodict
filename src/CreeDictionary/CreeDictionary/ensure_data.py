"""
Ensure the database -- especially the test database -- has certain requisite data.
"""

import logging


logger = logging.getLogger(__name__)


# Maps text with (legacy) part-of-speech to a paradigm.
# See res/layouts/static for a list of valid paradigms.
# Last updated: 2021-05-10
WORDFORM_TO_PARADIGM = [
    # Personal pronouns
    ("niya", "PRON", "personal-pronouns"),
    ("kiya", "PRON", "personal-pronouns"),
    ("wiya", "PRON", "personal-pronouns"),
    ("niyanân", "PRON", "personal-pronouns"),
    ("kiyânaw", "PRON", "personal-pronouns"),
    ("kiyawâw", "PRON", "personal-pronouns"),
    ("wiyawâw", "PRON", "personal-pronouns"),
    # Animate demonstratives
    ("awa", "PRON", "demonstrative-pronouns"),
    ("ana", "PRON", "demonstrative-pronouns"),
    ("nâha", "PRON", "demonstrative-pronouns"),
    ("ôki", "PRON", "demonstrative-pronouns"),
    ("aniki", "PRON", "demonstrative-pronouns"),
    ("nêki", "PRON", "demonstrative-pronouns"),
    # Inanimate demonstratives
    ("ôma", "PRON", "demonstrative-pronouns"),
    ("ôhi", "PRON", "demonstrative-pronouns"),
    ("anima", "PRON", "demonstrative-pronouns"),
    ("anihi", "PRON", "demonstrative-pronouns"),
    ("nêma", "PRON", "demonstrative-pronouns"),
    ("nêhi", "PRON", "demonstrative-pronouns"),
    # Inanimate/Obviative inanimate demonstratives
    ("ôhi", "PRON", "demonstrative-pronouns"),
    ("anihi", "PRON", "demonstrative-pronouns"),
    ("nêhi", "PRON", "demonstrative-pronouns"),
]


def ensure_wordform_paradigms():
    """
    Ensures that at least one Wordform object has a paradigm.
    """
    from CreeDictionary.API.models import Wordform

    if Wordform.objects.exclude(paradigm=None).exists():
        # Has paradigms; don't bother updating
        logger.info("there's at least one wordform with a paradigm; skipping update")
        return

    to_update = set_paradigm_for_demonstrative_and_personal_pronouns(
        Wordform.objects.all()
    )
    Wordform.objects.bulk_update(to_update, ["paradigm"])


def set_paradigm_for_demonstrative_and_personal_pronouns(query_set):
    """
    Given a query set of Wordform objects, updates all wordforms with a paradigm field.

    Does NOT .save() or commit the objects to the database! You have to do that with the
    list of returned objects.

    Why does this object not directly use the Wordform class/model?
    Because this function could be imported **before** Django could initialize the
    database models (e.g., in migrations). The **caller** is completely reponsible for
    providing the appropriate query_set and commiting the updates to the database.
    """
    objects_to_update = []

    for text, pos, paradigm in WORDFORM_TO_PARADIGM:
        for wordform in query_set.filter(text=text, pos=pos):
            if wordform.paradigm:
                logger.info(
                    "Not replacing existing paradigm %r on %r",
                    wordform.paradigm,
                    wordform,
                )
                continue
            wordform.paradigm = paradigm
            objects_to_update.append(wordform)

    return objects_to_update
