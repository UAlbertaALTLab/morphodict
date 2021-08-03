from pytest_django.fixtures import django_db_setup

# Make sure we are using the default in-memory database setup for import tests
django_db_setup = django_db_setup
