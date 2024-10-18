import json
import logging
import secrets
from argparse import ArgumentParser, BooleanOptionalAction

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Ensure there is a ‘cypress’ admin user

    This user is for running cypress tests that require a login. The password is
    saved in a JSON file to be read by cypress tests.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="""
                Make the user a superuser. Handy for development. Note: omitting
                this option will not remove the superuser bit if the cypress
                user is already a superuser.
            """,
        )

    def handle(self, superuser=False, **options):
        if not settings.USE_TEST_DB:
            logger.warning(
                "USE_TEST_DB is not set. You usually want to run this against the test DB."
            )

        cypress_user, created = User.objects.get_or_create(username="cypress")

        user_file_valid = False
        user_info_file = (
            settings.BASE_DIR.parent.parent / "cypress" / ".cypress-user.json"
        )

        password = None
        if user_info_file.exists():
            user_info = json.loads(user_info_file.read_text())
            # If there is an existing password in the JSON file, use it later so
            # that the same JSON file can be used by cypress tests against both
            # dev and test databases.
            password = user_info.get("password", "")
            if password and cypress_user.check_password(password):
                user_file_valid = True

        if (
            created
            or not user_file_valid
            or superuser
            and not cypress_user.is_superuser
        ):
            if not password:
                password = secrets.token_hex(20)
            user_info_file.write_text(
                json.dumps({"username": "cypress", "password": password}, indent=2)
                + "\n"
            )
            cypress_user.set_password(password)
            # Our only login page is the admin login page, which only accepts logins
            # from staff users.
            cypress_user.is_staff = True
            cypress_user.is_superuser = superuser
            cypress_user.save()
