# Docker for morphodict

The morphodict dictionaries are deployed on a single host with docker-compose.

Here's how it works!

## Overview

This `docker-compose.yml` is intended to run on production.

    # Runs production by default:
    docker-compose up

The containers will expose **ports like 8010** to the machine. See
the [application registry] and <settings.py>.

[application registry]: https://github.com/UAlbertaALTLab/deploy.altlab.dev/blob/master/docs/application-registry.tsv

## Development

We don’t currently have a docker setup intended for normal development
work. Developers generally check out and edit the code and run it the
old-fashioned way without any containers on Linux or macOS.

## Staging

If you want to try the docker-compose configuration locally before
trying it on production, use **staging**:

    ./helper.py staging up

Use this environment to test the Docker deployment _before_ pushing to
production. It will build a docker container that is essentially the same
as what will run in production, and will use the normal paths inside your
local code checkout for resources and databases.

On linux, the app may be unable to write to the database unless you
add a `docker-compose.override.yml` file to run morphodict inside the
container with the same UID that you use for development.

    version: "3"

    services:
      itwewina:
        user: "$YOUR_LOCAL_NUMERIC_USER_ID_EG_1000"

The staging setup *can* be made to work on Docker for Mac, but there are
some subtle differences in how users and mount permissions are handled
between Docker for Mac and docker on linux. Using docker on linux for
staging is recommended, as that’s closer to the production setup, so there
will be fewer surprises when shifting to production.

If you want to run the Cypress tests on the staging container, use
the following:

     CYPRESS_BASE_URL=http://localhost:8001 npx cypress open

See: https://docs.cypress.io/guides/guides/environment-variables.html#We-can-move-this-into-a-Cypress-environment-variable

When satisfied with the Docker environment used in staging, move it to
production:

## Production

The containers run on itw.altlab.dev, with nginx on the altlab.dev
gateway machine proxying traffic to it.

The production machines run relatively recent releases of Ubuntu LTS.

The docker image is automatically built and uploaded by github actions as
[ghcr.io/ualbertaaltlab/itwewina.altlab.app:latest](https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/pkgs/container/itwewina.altlab.app).
But you can also build it locally, and tag your local build as the ghcr one
as well in a pinch.

### Users and groups

There are two users: morphodict and morphodict-run. The morphodict user is
a regular UNIX user that owns the git checkout, has access to docker, and
which people can sudo to for interaction with the production deploy.

The other is a much more limited user used for running the container. In
case something goes wrong inside the container, it should have limited
access to a few data directories, and no other privileges.

There are also groups with the same names, `morphodict` and
`morphodict-run`. The `morphodict` user belongs to both groups so that it
do setup, configuration, and debugging; the `morphodict-run` user belongs
*only* to the `morphodict-run` group since it should have as few privileges
as possible.

In general, you should interact with the production deployment by
using `sudo` to run commands as `morphodict`.

Feel free to add yourself to the `morphodict` and `morphodict-run` groups
to more easily poke at 

### Deployment on `altlab-itw`




###

`docker/helper.py` encapsulates a bunch of knowlege
around

Because of how Docker works, these next `manage.py` commands can only work
if the container is already running.

  - Create the initial schema with:

        ./docker-django-manage.py migrate

  - Populate the test dictionary with

        ./docker-django-manage.py xmlimport \
            ../src/CreeDictionary/res/test_dictionaries/crkeng.xml

