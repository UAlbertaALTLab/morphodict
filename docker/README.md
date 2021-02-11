# Docker for itwêwina

The current setup was created with the intent of using it in production,
not for development.

Here are the steps that `make` will run:

  - Run `sqlite3 db.sqlite3 VACUUM` to create an empty database file

    Otherwise `docker-compose` will create a *directory* instead

  - Run `docker-compose up --build` to get itwêwina running on port 8000

Because of how Docker works, these next `manage.py` commands can only work
if the container is already running.

  - Create the initial schema with:

        ./docker-django-manage.py migrate

  - Populate the test dictionary with

        ./docker-django-manage.py xmlimport import \
            ../CreeDictionary/res/test_dictionaries/crkeng.xml

## On the `altlab-itw`

We created a **system user** called `itwewina`, which is part of the
`itwewina` and `docker` groups. The user's home directory is
`/opt/docker-compose/itwewina` and the repo is cloned there.

On `altlab-itw`, you will need to copy over the systemd unit file:

    sudo make unit-file

And then enable the service:

    sudo systemctl reload-daemo
    sudo systemctl enable docker-compose-itwewina

## Future work

  - smaller Docker image without dev dependencies through multi-stage
    builds
