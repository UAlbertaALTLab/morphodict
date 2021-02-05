# Docker for itwêwina

The current setup was created with the intent of using it in production,
not for development.

  - Run `sqlite3 db.sqlite3` to create an empty database file

    Otherwise `docker-compose` will create a *directory* instead

  - Run `docker-compose up --build` to get itwêwina running on port 8000

Because of how docker works, these next `manage.py` commands can only work
if the container is already running.

  - Create the initial schema with:

        ./docker-django-manage.py migrate

  - Populate the test dictionary with

        ./docker-django-manage.py xmlimport import \
            ../CreeDictionary/res/test_dictionaries/crkeng.xml

## Future work

  - smaller docker image without dev dependencies through multi-stage
    builds
