#!/bin/bash

# -f so that it's OK when there are no migrations to start with
rm -f CreeDictionary/API/migrations/*.py
touch CreeDictionary/API/migrations/__init__.py
pipenv run python CreeDictionary/manage.py makemigrations API
