import json
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from API.models import Definition, Wordform
from utils import shared_res_dir


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
        add_some_auto_translations()
        ensure_cypress_admin_user()


def import_test_dictionary():
    if Wordform.objects.count() == 0:
        print("No wordforms found, generating")
        call_command(
            "xmlimport",
            "import",
            shared_res_dir / "test_dictionaries" / "crkeng.xml",
        )


def add_some_auto_translations():
    if not Definition.objects.filter(auto_translation_source__isnull=False).exists():
        call_command("translatewordforms", wordforms=["acâhkosa"])


def ensure_cypress_admin_user():
    cypress_user, created = User.objects.get_or_create(username="cypress")

    user_file_valid = False
    user_info_file = settings.BASE_PATH / ".cypress-user.json"
    if user_info_file.exists():
        user_info = json.loads(user_info_file.read_text())
        if cypress_user.check_password(user_info.get("password", "")):
            user_file_valid = True

    if created or not user_file_valid:
        password = secrets.token_hex(20)
        user_info_file.write_text(
            json.dumps({"username": "cypress", "password": password}, indent=2) + "\n"
        )
        cypress_user.set_password(password)
        # Our only login page is the admin login page, which only accepts logins
        # from staff users.
        cypress_user.is_staff = True
        cypress_user.save()
