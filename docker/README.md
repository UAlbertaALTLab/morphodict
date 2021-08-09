# Docker for morphodict

The morphodict dictionaries are deployed on a single host with docker-compose.

Here's how it works!

## Overview

This `docker-compose.yml` is intended to run on production.

    # Runs production by default:
    docker-compose up

The containers will expose **ports like 8001** to the machine. See
the [application registry] and <settings.py>.

[application registry]: https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv

## Staging

If you want to try the docker-compose configuration locally before
trying it on production, use **staging**:

    ./manager.py staging

Use this environment to test the Docker deployment _before_ pushing to
production. It should use the actual Docker image used in production,
with few modifications.

It *can* be made to work on Docker for Mac, but there are some subtle
differences in how users and mount permissions are handled between Docker for
Mac and docker on linux. Using docker on linux for staging is recommended, as
that’s closer to the production setup, so there will be fewer surprises when
shifting to production.
    
If you want to run the Cypress tests on the staging container, use
the following:

     CYPRESS_BASE_URL=http://localhost:8001 npx cypress open

See: https://docs.cypress.io/guides/guides/environment-variables.html#We-can-move-this-into-a-Cypress-environment-variable

When satisfied with the Docker environment used in staging, move it to
production:

## Production

Please refer to the `Makefile` for the files that must be created before
`docker-compose up --build` can be run.

Because of how Docker works, these next `manage.py` commands can only work
if the container is already running.

  - Create the initial schema with:

        ./docker-django-manage.py migrate

  - Populate the test dictionary with

        ./docker-django-manage.py xmlimport \
            ../src/CreeDictionary/res/test_dictionaries/crkeng.xml

## Deployment on `altlab-itw`

There are two users: morphodict and morphodict-run. One is a regular UNIX user
that owns the git checkout, has access to docker, and which people can sudo to
for interaction with the production deploy.

The other is a much more limited user used for running the container. In case
something goes wrong inside the container, it should have limited access to a
few data directories, and no other privileges.


We created a **system user** called `itwewina`, which is part of the
`itwewina` and `docker` groups. The user's home directory is
`/opt/docker-compose/itwewina` and the repo is cloned there.

On `altlab-itw`, you will need to copy over the `systemd` unit file:

    sudo make unit-file

And then enable the service:

    sudo systemctl daemon-reload
    sudo systemctl enable docker-compose-itwewina
