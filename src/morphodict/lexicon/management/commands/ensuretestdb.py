from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from morphodict.cvd import definition_vectors_path
from morphodict.lexicon import DEFAULT_TEST_IMPORTJSON_FILE


class Command(BaseCommand):
    help = """Ensure that the test db exists and is properly set up.

    If it does not exist, it will be created. If it needs to be migrated, it
    will be migrated. If assorted other things need to be in there, they will be
    added if missing.
    """

    def handle(self, *args, **options):
        from morphodict.lexicon.models import Wordform

        assert settings.USE_TEST_DB

        call_command("migrate", verbosity=0)

        def importjson_newer_than_db():
            return (
                not settings.TEST_DB_FILE.exists()
                or DEFAULT_TEST_IMPORTJSON_FILE.stat().st_mtime
                > settings.TEST_DB_FILE.stat().st_mtime
            )

        if (
            not Wordform.objects.exists()
            or not definition_vectors_path().exists()
            or importjson_newer_than_db()
        ):
            call_command("importjsondict", purge=True, atomic=True)
        call_command("ensurecypressadminuser")
