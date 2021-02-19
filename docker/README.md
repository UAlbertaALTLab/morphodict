# Docker for itwêwina

The current setup was created with the intent of using it in production,
not for development.

The `itwewina` container will expose **port 8001** to the machine.

Please refer to the `Makefile` for the files that must be created before
`docker-compose up --build` can be run.

Because of how Docker works, these next `manage.py` commands can only work
if the container is already running.

  - Create the initial schema with:

        ./docker-django-manage.py migrate

  - Populate the test dictionary with

        ./docker-django-manage.py xmlimport import \
            ../CreeDictionary/res/test_dictionaries/crkeng.xml

## Deployment on `altlab-itw`

We created a **system user** called `itwewina`, which is part of the
`itwewina` and `docker` groups. The user's home directory is
`/opt/docker-compose/itwewina` and the repo is cloned there.

On `altlab-itw`, you will need to copy over the `systemd` unit file:

    sudo make unit-file

And then enable the service:

    sudo systemctl daemon-reload
    sudo systemctl enable docker-compose-itwewina
