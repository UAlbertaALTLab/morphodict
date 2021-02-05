FROM python:3.9-slim-buster

LABEL maintainer="Eddie Antonio Santos <Eddie.Santos@nrc-cnrc.gc.ca>"

# (2021-01-15): This Dockerfile was derived from Gūnáhà:
#  - https://github.com/UAlbertaALTLab/gunaha/blob/master/Dockerfile
#
# Changes:
#
#  - use Gunicorn instead of uwsgi; I'm not sure why I chose uwsgi for Gūnáhà,
#    but I've got itwêwina working with Gunicorn, so I'm gonna stick with that
#


# Directories:
#
# /app — the app code will live here
#

# Choose an ID that will be consistent across all machines in the network
# To avoid overlap with user IDs, use an ID over
# /etc/login.defs:/UID_MAX/, which defaults to 60,000
ARG UID_GID=60002
ARG WSGI_USER=itwewina
ARG EXPOSE_PORT=8000

# Create the user/group for the application
RUN groupadd --system --gid ${UID_GID} ${WSGI_USER} \
 && useradd --no-log-init --system --gid ${WSGI_USER} --uid ${UID_GID} ${WSGI_USER} --create-home

# TODO: move package.json dependences from build and test
#  - [ ] must document in development guide

# Install and build dependencies,
# then remove build-time dependencies to keep the image slim!
RUN set -ex \
 && BUILD_DEPS=" \
    build-essential \
    tini \
    nodejs \
    npm \
    moreutils `# for sponge` \
    " \
 && apt-get update \
 && apt-get install -y --no-install-recommends $BUILD_DEPS \
 && pip install pipenv \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /data/ /app/ \
 && chown ${WSGI_USER} /data /app

USER ${WSGI_USER}

WORKDIR /app/

# Setup Python deps
ADD --chown=${WSGI_USER} Pipfile .
ADD --chown=${WSGI_USER} Pipfile.lock .

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

ADD --chown=${WSGI_USER} package.json .
ADD --chown=${WSGI_USER} package-lock.json .
# cypress is a big, heavy package that takes a long time to install and
# that we absolutely don’t need in production
RUN grep -Ev '"@?cypress' package.json | sponge package.json

RUN npm install

# Copy the application files. Make sure .dockerignore is setup properly so it
# doesn't copy unnecessary files
ADD --chown=${WSGI_USER} . /app/

RUN NODE_ENV=production npm run build

# Gunicorn will listen on this port:
EXPOSE ${EXPOSE_PORT}

# Among other things -- see
# https://github.com/krallin/tini#tini---a-tiny-but-valid-init-for-containers
# -- this makes typing Ctrl-C into docker-compose work
ENTRYPOINT ["tini", "--"]

WORKDIR /app/CreeDictionary
ENV EXPOSE_PORT=${EXPOSE_PORT}
CMD /app/.venv/bin/gunicorn \
    --access-logfile - \
    --bind 0.0.0.0:${EXPOSE_PORT} \
    CreeDictionary.wsgi:application
