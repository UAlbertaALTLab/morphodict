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
ARG UID_GID=60003
ARG EXPOSE_PORT=8000

# Create the user/group for the application
RUN groupadd --system --gid ${UID_GID} itwewina \
 && useradd --no-log-init --system --gid itwewina --uid ${UID_GID} itwewina --create-home

# TODO: move package.json dependences from build and test
#  - [ ] must document in development guide

# Install and build dependencies,
# then remove build-time dependencies to keep the image slim!
RUN set -ex \
 && BUILD_DEPS=" \
    build-essential \
    tini \
    moreutils `# for sponge` \
    gnupg `# for verifying nodesource certificate` \
    " \
 && apt-get update \
 && apt-get install -y --no-install-recommends $BUILD_DEPS \
 && pip install pipenv \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /data/ /app/ \
 && chown itwewina /data /app

# Install Node + npm
# (note: default npm is too old for the apt-install'd version of NodeJS??!?!?!)
# Using instructions from: https://github.com/nodesource/distributions/blob/master/README.md#manual-installation
WORKDIR /tmp
COPY docker/nodesource.gpg.key .
RUN set -ex \
    && VERSION=node_12.x \
    && DISTRO="buster" `# must be in sync with Dockerfile` \
    && apt-key add nodesource.gpg.key \
    && (echo "deb https://deb.nodesource.com/$VERSION $DISTRO main" | tee /etc/apt/sources.list.d/nodesource.list) \
    && (echo "deb-src https://deb.nodesource.com/$VERSION $DISTRO main" | tee -a /etc/apt/sources.list.d/nodesource.list) \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs

USER itwewina

WORKDIR /app/

# Setup Python deps
ADD --chown=itwewina Pipfile .
ADD --chown=itwewina Pipfile.lock .

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

ADD --chown=itwewina package.json .
ADD --chown=itwewina package-lock.json .
# cypress is a big, heavy package that takes a long time to install and
# that we absolutely don’t need in production
RUN grep -Ev '"@?cypress' package.json | sponge package.json

RUN npm install

# Copy the application files. Make sure .dockerignore is setup properly so it
# doesn't copy unnecessary files
ADD --chown=itwewina . /app/

RUN NODE_ENV=production npm run build \
 && /app/.venv/bin/python CreeDictionary/manage.py collectstatic --noinput

# Gunicorn will listen on this port:
EXPOSE ${EXPOSE_PORT}

# Among other things -- see
# https://github.com/krallin/tini#tini---a-tiny-but-valid-init-for-containers
# -- this makes typing Ctrl-C into docker-compose work
ENTRYPOINT ["tini", "--"]

WORKDIR /app/CreeDictionary
ENV EXPOSE_PORT=${EXPOSE_PORT}


ENV DEBUG=True
ENV ENABLE_DJANGO_DEBUG_TOOLBAR=False
CMD /app/.venv/bin/gunicorn \
    --access-logfile - \
    --bind 0.0.0.0:${EXPOSE_PORT} \
    CreeDictionary.wsgi:application
