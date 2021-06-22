from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from CreeDictionary.cvd import definition_vectors_path
from CreeDictionary.utils import shared_res_dir
from morphodict.lexicon.models import Wordform, Definition
from morphodict.lexicon.test_db import TEST_DB_IMPORTJSON


class Command(BaseCommand):
    help = """Ensure that the test db exists and is properly set up.

    If it does not exist, it will be created. If it needs to be migrated, it
    will be migrated. If assorted other things need to be in there, they will be
    added if missing.
    """

    def handle(self, *args, **options):
        assert settings.USE_TEST_DB

        call_command("migrate", verbosity=0)

        call_command(
            "importjsondict",
            TEST_DB_IMPORTJSON,
        )
        call_command("translatewordforms")
        call_command("ensurecypressadminuser")

        if not definition_vectors_path().exists():
            call_command("builddefinitionvectors")
