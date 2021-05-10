import json
import secrets

from API.models import Definition, Wordform
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from utils import shared_res_dir

from CreeDictionary.ensure_data import ensure_wordform_paradigms


class Command(BaseCommand):
    help = """Ensure that the test db exists and is properly set up.

    If it does not exist, it will be created. If it needs to be migrated, it
    will be migrated. If assorted other things need to be in there, they will be
    added if missing.
    """

    def handle(self, *args, **options):
        assert settings.USE_TEST_DB

        call_command("migrate", verbosity=0)

        import_test_dictionary()
        ensure_wordform_paradigms()
        add_some_auto_translations()
        call_command("ensurecypressadminuser")


def import_test_dictionary():
    if Wordform.objects.count() == 0:
        print("No wordforms found, generating")
        call_command(
            "xmlimport",
            shared_res_dir / "test_dictionaries" / "crkeng.xml",
        )


def add_some_auto_translations():
    if not Definition.objects.filter(auto_translation_source__isnull=False).exists():
        call_command("translatewordforms", wordforms=["acâhkosa"])
