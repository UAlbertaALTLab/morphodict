# Docker for itwêwina

itwêwina.altlab.app is deployed on a single host with docker-compose.

Here's how it works!

## Overview

This folder uses [multiple compose files][] so that configuration can be
shared upon in [staging][] and production environments.

[multiple compose files]: https://docs.docker.com/compose/extends/#multiple-compose-files
[staging]: https://en.wikipedia.org/wiki/Deployment_environment#Staging

The shared configuration is in `docker-compose.yml`.

**`docker-compose.yml` is not a complete configuration by itself**.

Instead, this file **MUST** be combined with either `./staging.yml`
or `./production.yml`, depending on your configuration:

    # Staging
    docker-compose -f docker-compose.yml -f staging.yml up
    # Production
    docker-compose -f docker-compose.yml -f production.yml up

For convenience, `docker-compose.override.yml` is a symlink to
`production.yml`. This means that `docker-compose up` with no `-f`
arguments will start the production environment by default.

    # Runs production by default:
    docker-compose up

The `itwewina` container will expose **port 8001** to the machine. See
the [application registry]!

[application registry]: https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv

## Staging

Use this environment to test the Docker deployment _before_ pushing to
production. It should use the actual Docker image used in production,
with few modifications.

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
