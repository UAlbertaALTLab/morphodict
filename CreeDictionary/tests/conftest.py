# todo: database fixture
# https://pytest-django.readthedocs.io/en/latest/database.html#populate-the-database-with-initial-test-data
# import pytest
#
# from django.core.management import call_command
#
# @pytest.fixture(scope='session')
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         call_command('loaddata', 'your_data_fixture.json')
